# -*- mode: python; python-indent: 4 -*-
import ipaddress

import ncs
from ncs.application import NanoService
from resource_manager.service import Allocator


class CreateRfs(NanoService):
    @NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, compproplist):
        self.log.info('Service create(service=', service._path, ')')

        if not (service.left_router < service.right_router):
            raise ValueError("Left side router must precede right side router in alphabetical ascending order. Please swap left and right side.")

        ALLOCATION_NAME = f"{service.left_router} [{service.left_interface}] <-> {service.right_router} [{service.right_interface}]"

        allocator = Allocator(service)
        service.vars.ipv4_prefix = (allocator
                                    .ip(service.custom.ipv4_prefix)
                                    .pool('ipv4-backbone-link')
                                    .prefix_length(31)
                                    .allocate(ALLOCATION_NAME))
        service.vars.ipv6_prefix = (allocator
                                    .ip(service.custom.ipv6_prefix)
                                    .pool('ipv6-backbone-link')
                                    .prefix_length(126)
                                    .allocate(ALLOCATION_NAME))
        self.log.info('Allocated IPv4 prefix:', service.vars.ipv4_prefix)
        self.log.info('Allocated IPv6 prefix:', service.vars.ipv6_prefix)

        vars = ncs.template.Variables()
        vars.add('CR', 'true')

        left_router = service._parent._parent.router[service.left_router]
        right_router = service._parent._parent.router[service.right_router]
        left_roles = set([role.name.string for role in left_router.role])
        right_roles = set([role.name.string for role in right_router.role])
        self.log.info('Left roles:', left_roles)
        self.log.info('Right roles:', right_roles)
        if 'core' in left_roles and 'core' in right_roles:
            # Core links are always full-mesh and that's already handled by
            # ibgp_fullmesh.py
            service.vars.left_ibgp_type = 'none'
            service.vars.right_ibgp_type = 'none'
        elif 'core' in left_roles and 'edge' in right_roles:
            service.vars.left_ibgp_type = 'rr-client'
            service.vars.right_ibgp_type = 'direct'

        service.vars.left_ipv4_loopback_address = left_router.vars.ipv4_address
        service.vars.left_ipv6_loopback_address = left_router.vars.ipv6_address
        service.vars.right_ipv4_loopback_address = right_router.vars.ipv4_address
        service.vars.right_ipv6_loopback_address = right_router.vars.ipv6_address

        ipv4prefix = ipaddress.IPv4Network(service.vars.ipv4_prefix)
        # get first available IP address in the subnet, for /31 we use the network address
        if ipv4prefix.prefixlen == 31:
            service.vars.left_ipv4_address = ipv4prefix.network_address
            service.vars.right_ipv4_address = ipv4prefix.network_address + 1
        else:
            service.vars.left_ipv4_address = ipv4prefix.network_address + 1
            service.vars.right_ipv4_address = ipv4prefix.network_address + 2
        service.vars.ipv4_prefix_length = ipv4prefix.prefixlen

        ipv6prefix = ipaddress.IPv6Network(service.vars.ipv6_prefix)
        # get first available IP address in the subnet, for /31 we use the network address
        if ipv6prefix.prefixlen == 127:
            service.vars.left_ipv6_address = ipv6prefix.network_address
            service.vars.right_ipv6_address = ipv6prefix.network_address + 1
        else:
            service.vars.left_ipv6_address = ipv6prefix.network_address + 1
            service.vars.right_ipv6_address = ipv6prefix.network_address + 2
        service.vars.ipv6_prefix_length = ipv6prefix.prefixlen

        template = ncs.template.Template(service)
        template.apply('cfs-backbone-link', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.register_nano_service(servicepoint='netinfra-backbone-link-servicepoint',
                                   componenttype='ncs:self',
                                   state='netinfra:backbone-link-create-rfs',
                                   nano_service_cls=CreateRfs)

    def teardown(self):
        pass
