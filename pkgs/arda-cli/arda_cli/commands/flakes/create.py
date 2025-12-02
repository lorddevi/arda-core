"""Create new Arda world using flakes."""

import shlex
import subprocess
import sys
from pathlib import Path
from shutil import copytree

import click
import rich_click as rclick
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from arda_cli.lib.output import get_output_manager


@click.command()
@click.argument("name")
@click.option(
    "--template",
    default="default",
    help="Template to use for the new world",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force creation even if directory exists",
)
@click.pass_context
def create(ctx: click.Context, name: str, template: str, force: bool) -> None:
    """Create a new Arda world.

    This creates a new flake-based Arda installation in a new directory.

    NAME is the name of the world to create.
    """
    output = get_output_manager(ctx)

    # Validate world name
    if not name.replace("-", "").replace("_", "").isalnum():
        output.error(
            f"Invalid world name '{name}'. "
            "Use only letters, numbers, hyphens, and underscores."
        )
        sys.exit(1)

    # Determine target directory
    target_dir = Path(name).absolute()

    # Check if directory exists
    if target_dir.exists() and not force:
        output.error(
            f"Directory '{target_dir}' already exists. "
            f"Use --force to overwrite or choose a different name."
        )
        sys.exit(1)

    # Get template path - templates are in arda-core/templates/arda/
    # Following clan-core's pattern: templates are copied into the package
    # at arda_core_templates/arda during the Nix build process

    # Try development path first (running from source)
    arda_core_root = Path(__file__).parent.parent.parent.parent.parent.parent
    dev_templates_dir = arda_core_root / "templates" / "arda"

    # Try installed package path (templates copied into package)
    # In Nix-built packages, templates are copied to:
    #   $out/lib/python3.13/site-packages/arda_cli/arda_core_templates
    # Navigate from this module to find templates in the Nix store
    # __file__ = .../site-packages/arda_cli/commands/flakes/create.py
    # Go up 7 levels to package root, then down to templates
    installed_templates_dir = (
        Path(__file__).parent.parent.parent.parent.parent.parent.parent
        / "lib"
        / "python3.13"
        / "site-packages"
        / "arda_cli"
        / "arda_core_templates"
        / "arda"
    )

    # Choose the right templates directory
    if dev_templates_dir.exists():
        templates_dir = dev_templates_dir
    elif installed_templates_dir.exists():
        templates_dir = installed_templates_dir
    else:
        output.error(
            f"Template directory not found. "
            f"Checked: {dev_templates_dir} and {installed_templates_dir}"
        )
        sys.exit(1)

    template_path = templates_dir / template

    if not template_path.exists():
        output.error(f"Template '{template}' not found at {template_path}")
        output.info("Available templates: default")
        sys.exit(1)

    console = Console()

    # Confirm creation
    if not force:
        if not Confirm.ask(
            f"Create new Arda world '{name}' at {target_dir}?",
            default=True,
            console=console,
        ):
            output.info("World creation cancelled.")
            sys.exit(0)

    # Create the world
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating world...", total=None)

            # 1. Remove directory if it exists
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)

            # 2. Copy template
            progress.update(task, description="Copying template files...")
            copytree(str(template_path), str(target_dir))

            # 3. Recursively make all files and directories writable
            # This ensures that files from the Nix store can be modified/deleted
            # CRITICAL: This must happen BEFORE git init, otherwise git can't
            # create .git directory
            progress.update(task, description="Making files writable...")
            import os
            import stat

            # Make target directory writable FIRST
            # Use 755 (rwxr-xr-x) for directories: owner full access, others
            # read/execute
            target_dir.chmod(
                stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
            )

            # Then recursively chmod all files and subdirectories
            for root, dirs, files in os.walk(target_dir):
                for d in dirs:
                    dir_path = Path(root) / d
                    # Directories: 755 (rwxr-xr-x)
                    dir_path.chmod(
                        stat.S_IRWXU
                        | stat.S_IRGRP
                        | stat.S_IXGRP
                        | stat.S_IROTH
                        | stat.S_IXOTH
                    )
                for f in files:
                    file_path = Path(root) / f
                    # Files: 644 (rw-r--r--)
                    file_path.chmod(
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )

            # 4. Initialize git
            progress.update(task, description="Initializing git repository...")
            git_initialized = False

            # Clean up any existing .git file or directory
            # that might be left from failed init
            git_dir = target_dir / ".git"
            if git_dir.exists():
                try:
                    if git_dir.is_dir():
                        import shutil

                        shutil.rmtree(git_dir)
                    else:
                        git_dir.unlink()
                except Exception:
                    pass

            # Try to initialize git repository with regular init
            # This works even when running in a subdirectory of another git repo
            git_init_result = subprocess.run(
                ["git", "init"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                shell=False,
            )

            # Try to verify that git actually works by running rev-parse
            # This tells us if the repository was initialized successfully
            git_check = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                shell=False,
            )

            if git_check.returncode == 0:
                # Git commands work, so repository is initialized
                git_initialized = True
                if git_init_result.returncode == 0:
                    output.debug("Git repository initialized successfully")
                else:
                    output.debug(
                        "Git repository initialized (git had warnings but works)"
                    )
            else:
                # Git doesn't work, initialization failed
                git_initialized = False
                error_msg = git_init_result.stderr.strip()

                # Check if this is due to Nix sandbox restrictions
                if "Permission denied" in error_msg:
                    output.warning(
                        "Git repository not initialized due to Nix sandbox "
                        "restrictions. After the world is created, you can "
                        "manually run:\n"
                        f"  cd {name}\n"
                        f"  git init\n"
                        f"  git add .\n"
                        f"  git commit -m 'Initial {name} world'"
                    )
                else:
                    output.warning(
                        f"Could not initialize git repository. Error: {error_msg}"
                    )

            # If git was initialized, add files
            if git_initialized:
                try:
                    subprocess.run(
                        ["git", "add", "."],
                        cwd=target_dir,
                        capture_output=True,
                        shell=False,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    output.warning(f"Could not add files to git: {e}")
                    git_initialized = False

            # 5. Update flake (only run if git was initialized)
            if git_initialized:
                progress.update(task, description="Updating flake...")
                result = subprocess.run(
                    ["nix", "flake", "update"],
                    cwd=target_dir,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                if result.returncode != 0:
                    output.warning(
                        "Flake update had warnings (this is normal for first run)"
                    )

            # 6. Create initial commit (only if git was initialized)
            if git_initialized:
                progress.update(task, description="Creating initial commit...")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=target_dir,
                    capture_output=True,
                    shell=False,
                )
                # Use shlex.quote to safely escape the world name
                safe_name = shlex.quote(name)
                commit_result = subprocess.run(  # noqa: S603
                    ["git", "commit", "-m", f"Initial {safe_name} world"],
                    cwd=target_dir,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                if commit_result.returncode != 0:
                    output.warning(
                        "Could not create initial commit, but files are ready"
                    )

            # 7. Generate age keys if needed
            # Match clan-core's behavior: generate keys at ~/.config/sops/age/keys.txt
            # instead of inside the world directory, so git status stays clean
            progress.update(task, description="Setting up secrets...")
            xdg_config_home = os.getenv(
                "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
            )
            age_key_path = Path(xdg_config_home) / "sops" / "age" / "keys.txt"

            if not age_key_path.exists():
                try:
                    # Create the sops/age directory in user's config home
                    age_key_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        subprocess.run(  # noqa: S603
                            ["age-keygen", "-o", str(age_key_path)],
                            check=True,
                            capture_output=True,
                            text=True,
                            shell=False,
                        )
                        output.info(f"Generated age key at {age_key_path}")
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        output.warning(
                            f"Failed to generate age key: {e}. "
                            "You can install 'age' package if you plan to use "
                            "secrets management."
                        )
                except (PermissionError, OSError) as e:
                    output.warning(
                        f"Could not create sops config directory: {e}. "
                        "Skipping age key generation."
                    )

            progress.update(task, description="Done!")

        # Success message
        git_status = ""
        if not git_initialized:
            git_status = (
                "\n[yellow]Note:[/yellow] Git repository not initialized. "
                "Run 'git init' manually if needed.\n"
            )

        success_panel = Panel(
            f"Successfully created Arda world: [bold]{name}[/bold]\n\n"
            f"Location: [cyan]{target_dir}[/cyan]{git_status}\n"
            f"Next steps:\n"
            f"  • cd {name}\n"
            f"  • nix develop\n"
            f"  • arda help\n\n"
            f"[dim]See README.md in the world directory for more information.[/dim]",
            title="✅ World Created",
            border_style="green",
        )
        console.print(success_panel)

    except subprocess.CalledProcessError as e:
        output.error(f"Command failed: {e.cmd[0]}")
        if e.output:
            output.debug(f"Output: {e.output.decode()}")
        if e.stderr:
            output.debug(f"Error: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        output.error(f"Failed to create world: {e}")
        import traceback

        output.debug("Full traceback:")
        output.debug(traceback.format_exc())
        sys.exit(1)
