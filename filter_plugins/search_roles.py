class FilterModule(object):
    @staticmethod
    def search_roles(ludus, search_role):
        if not isinstance(ludus, list):
            return None
        for vm in ludus:
            if vm.get("roles") and isinstance(vm.get("roles"), list):
                for role in vm.get("roles"):
                    if isinstance(role, str) and search_role in role:
                        return vm
                    if isinstance(role, dict) and search_role in role.get("name", ""):
                        return vm
        return None

    def filters(self):
        return {
            "search_roles": self.search_roles
        }
