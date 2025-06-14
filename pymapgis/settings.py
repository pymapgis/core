from pathlib import Path
import toml
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)


# Define possible TOML file paths
PROJECT_TOML_FILE = Path(".pymapgis.toml")
USER_TOML_FILE = Path.home() / ".pymapgis.toml"


class _Settings(BaseSettings):
    cache_dir: str = "~/.cache/pymapgis"
    default_crs: str = "EPSG:4326"

    model_config = SettingsConfigDict(
        env_prefix="PYMAPGIS_", extra="ignore", env_file_encoding="utf-8"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = [
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        ]

        # Load TOML files
        # Process in order of increasing precedence for insertion: User TOML, then Project TOML.
        # Project TOML should override User TOML, so it needs to appear later in the sources list.
        toml_files_to_check = [USER_TOML_FILE, PROJECT_TOML_FILE]

        loaded_toml_sources = []
        for toml_file_path in toml_files_to_check:
            if toml_file_path.exists():
                try:
                    loaded_toml_sources.append(
                        TomlConfigSettingsSource(settings_cls, toml_file_path)
                    )
                except Exception as e:
                    # Handle potential errors during TOML file loading gracefully
                    print(
                        f"Warning: Could not load settings from {toml_file_path}: {e}"
                    )

        # Insert TOML sources after init_settings (index 0) and before other environment sources.
        # loaded_toml_sources will be in order [user_toml_source, project_toml_source] if both exist.
        # When inserted into the main sources list, project_toml_source will have higher precedence.
        # Example: sources starts as [init, env, dotenv, secret]
        # sources[1:1] = [user, project] results in [init, user, project, env, dotenv, secret]
        sources[1:1] = loaded_toml_sources

        # The old loop for reference - this had incorrect precedence ordering:
        # for toml_file_path in toml_files: # Original: [USER_TOML_FILE, PROJECT_TOML_FILE]
        #     if toml_file_path.exists():
        #         try:
        # # Create a TomlConfigSettingsSource for each TOML file
        # # We insert it after init_settings but before env_settings
        # # so that environment variables can override TOML files,
        # # and TOML files override defaults.
        # # Pydantic loads sources in order, with later sources overriding earlier ones.
        # # So, we want default -> toml -> env
        # # Default (init_settings) is at the start.
        # # We will insert TOML sources after default.
        # # Env sources (env_settings, dotenv_settings) come after TOML.
        # toml_source = TomlConfigSettingsSource(settings_cls, toml_file_path)
        # # Insert TOML source after init_settings (index 0)
        # # and before other sources like env_settings
        # sources.insert(1, toml_source) # This line caused issues with precedence order
        return tuple(sources)


settings = _Settings()
