# Service Discovery - Part 6 - No Discrepancies

The details for each makefile target is found in [tutorial.mk](/tutorial.mk) 
file.

## Overview

This will do service discovery on device ER-2. The service(s) will fully 
discovered and there is
no difference in the configurion on the device and the configuration in NSO.

**23. Find services in device ER-2**

Proceed with ER-2, which again has no diff.

```
make tutorial-sd-23-find-services-er-2
```

## NOTE
ER-2 and ER-3 also have `mtu 1600` on `eth3`; this is only covered because
patch set v2 (step 19) is already applied. Unlike ER-1, the `eth4`
vrf-interface service on ER-2 is created for the first time here, so the v2
default `mtu 1500` is likely pushed to the device by the find-services commit.
The original configuration is saved after find-services, so that change does
not show up in the diff. See
[limitations](../docs/framework/limitations.md#discovery-safety).
