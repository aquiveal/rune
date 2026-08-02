from pydantic import BaseModel


class ModuleSchema(BaseModel):
    name: str
    url: str
    path: str

    @property
    def specific_url(self) -> str:
        clean_url = self.url.strip()
        return clean_url.split(" ")[0] if " " in clean_url else clean_url

    @property
    def base_url(self) -> str:
        clean_url = self.url.strip()
        if " " in clean_url:
            return clean_url.split(" ")[1]
        if "/tree/" in clean_url:
            return clean_url.split("/tree/")[0]
        return clean_url

    @property
    def source_path(self) -> str:
        if "/tree/" in self.specific_url:
            parts = self.specific_url.split("/tree/")
            if len(parts) > 1:
                path_parts = parts[1].split("/", 1)
                if len(path_parts) > 1:
                    return path_parts[1]
        return ""

    @property
    def inferred_type(self) -> str:
        if "/modules/" in self.path or self.path.startswith("modules/"):
            return "modules"
        if "/rules/" in self.path or self.path.startswith("rules/"):
            return "rules"
        if "/skills/" in self.path or self.path.startswith("skills/"):
            return "skills"
        return "unknown"
