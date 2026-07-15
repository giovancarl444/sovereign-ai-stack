#!/usr/bin/env python3
"""
sovereign-ai-stack :: launch.py
Launch an Oracle Cloud A1.Flex (ARM) instance WITHOUT the 429 retry-storm and
WITHOUT wasting calls on availability domains that don't exist for your tenancy.

Why this exists:
  * The `oci` CLI *binary* ignores OCI_RETRY_STRATEGY and storm-retries internally,
    hanging 15-90s and burning your rate-limit budget. This script calls the OCI
    *SDK* directly, which honors OCI_RETRY_STRATEGY=none and returns instantly.
  * OCI returns "Out of host capacity" (a 500, not a 429) because A1.Flex is
    massively over-subscribed. The fix is patient retries across REAL ADs, not
    hammering. Most people probe AD-1/2/3 blindly; ADs that aren't yours just
    waste throttle. This discovers the ADs that actually belong to you.

Usage:
  pip install oci   # or use your oci-cli's bundled python
  export OCI_RETRY_STRATEGY=none
  python3 launch.py \
      --compartment ocid1.tenancy.oc1..xxxx \
      --image      ocid1.image.oc1.eu-stockholm-1.aaaaaaaa... \
      --subnet     ocid1.subnet.oc1.eu-stockholm-1.aaaaaaaa... \
      --ssh-key    ~/.ssh/id_ed25519.pub \
      --ocpus 8 --memory 64

On success it prints INSTANCE_ID / PUBLIC_IP. On capacity starvation it tells
you it's a capacity problem (keep retrying), not a code bug.
"""
import os
import sys
import json
import argparse
import datetime

try:
    import oci
except ImportError:
    sys.stderr.write(
        "ERROR: OCI SDK not found. Install it:\n"
        "  pip install oci\n"
        "or run this script with the python that ships the oci CLI, e.g.\n"
        "  /opt/homebrew/Cellar/oci-cli/*/libexec/bin/python launch.py ...\n"
    )
    sys.exit(2)

# Disable the SDK's own retry storm. The CLI binary ignores this; the SDK honors it.
os.environ["OCI_RETRY_STRATEGY"] = os.environ.get("OCI_RETRY_STRATEGY", "none")


def discover_ads(identity_client, compartment_id, region):
    """Return the availability domains that ACTUALLY belong to this tenancy."""
    c = oci.identity.IdentityClient(identity_client.base_client.config)
    c.base_client.set_region(region)
    try:
        ads = [a.name for a in c.list_availability_domains(compartment_id, retry_strategy=None).data]
        return ads
    except oci.exceptions.ServiceError as e:
        if e.status == 401:
            return []  # region not subscribed for this tenancy
        return [f"ERR_{e.status}_{e.code}"]


def classify(err_text):
    e = err_text.lower()
    if "out of host capacity" in e or "internalerror" in e or "outofhostcapacity" in e:
        return "CAPACITY"          # real starvation — keep waiting, it frees up
    if any(k in e for k in ("429", "toomanyrequests", "throttl", "limitexceeded", "quota")):
        return "THROTTLE"          # back off
    if "cannotparserequest" in e or "400" in e:
        return "BADREQ"            # real request-format bug — investigate
    return "OTHER"


def main():
    p = argparse.ArgumentParser(description="Patient A1.Flex launcher (no retry storm).")
    p.add_argument("--profile", default="DEFAULT")
    p.add_argument("--region", default=None, help="override config region")
    p.add_argument("--compartment", required=True)
    p.add_argument("--shape", default="VM.Standard.A1.Flex")
    p.add_argument("--ocpus", type=int, default=4)
    p.add_argument("--memory", type=int, default=24)
    p.add_argument("--image", required=True)
    p.add_argument("--subnet", required=True)
    p.add_argument("--ssh-key", required=True)
    p.add_argument("--name", default="sovereign-node")
    args = p.parse_args()

    cfg = oci.config.from_file(profile_name=args.profile)
    region = args.region or cfg.get("region")
    if not region:
        sys.stderr.write("ERROR: no --region and none in ~/.oci/config\n")
        sys.exit(2)

    with open(os.path.expanduser(args.ssh_key)) as f:
        ssh_key = f.read().strip()

    ic = oci.identity.IdentityClient(cfg)
    ads = discover_ads(ic, args.compartment, region)
    ads = [a for a in ads if not str(a).startswith("ERR")]
    if not ads:
        sys.stderr.write(f"ERROR: no availability domains discovered for {region}. "
                         f"Subscribe the region in OCI console 'Region Management' first.\n")
        sys.exit(3)

    print(f"discovered ADs for {region}: {ads}")

    cc = oci.core.ComputeClient(cfg)
    cc.base_client.set_region(region)

    last_status = None
    for ad in ads:
        details = oci.core.models.LaunchInstanceDetails(
            availability_domain=ad,
            compartment_id=args.compartment,
            shape=args.shape,
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=args.ocpus, memory_in_gbs=args.memory),
            display_name=args.name,
            source_details=oci.core.models.InstanceSourceViaImageDetails(image_id=args.image),
            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=args.subnet, assign_public_ip=True),
            metadata={"ssh_authorized_keys": ssh_key},
        )
        try:
            r = cc.launch_instance(launch_instance_details=details, retry_strategy=None)
            inst = r.data
            print("OK")
            print("INSTANCE_ID", inst.id)
            print("AD", ad)
            print("STATE", inst.lifecycle_state)
            json.dump({"id": inst.id, "ad": ad, "state": inst.lifecycle_state},
                      open("/tmp/sovereign_instance.json", "w"), default=str)
            return 0
        except oci.exceptions.ServiceError as e:
            last_status = classify(e.message)
            print(f"[{ad}] {last_status}: {e.code} — {e.message[:160]}")
            if last_status == "BADREQ":
                sys.stderr.write("FORMAT ERROR — check your OCIDs/image/subnet. Not a capacity issue.\n")
                return 4

    print(f"\nAll {len(ads)} AD(s) returned: {last_status}.")
    if last_status == "CAPACITY":
        print("This is HOST CAPACITY starvation, not a bug. OCI frees A1.Flex hosts constantly.")
        print("Retry on a schedule (cron every 20-30 min). The first free host wins.")
        print("Full automated watcher + multi-region fallback is in the paid kit.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
