"""VM-related exceptions for testing."""


class VMError(Exception):
    """Base exception for VM operations."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause
        self.message = message

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message}: {self.cause}"
        return self.message


class VMNotFoundError(VMError):
    """Raised when a VM is not found."""

    def __init__(self, vm_name: str):
        super().__init__(f"VM '{vm_name}' not found")
        self.vm_name = vm_name


class VMCreateError(VMError):
    """Raised when VM creation fails."""

    def __init__(self, vm_name: str, cause: Exception | None = None):
        super().__init__(f"Failed to create VM '{vm_name}'", cause)
        self.vm_name = vm_name


class VMStartError(VMError):
    """Raised when VM start fails."""

    def __init__(self, vm_name: str, cause: Exception | None = None):
        super().__init__(f"Failed to start VM '{vm_name}'", cause)
        self.vm_name = vm_name


class VMStopError(VMError):
    """Raised when VM stop fails."""

    def __init__(self, vm_name: str, cause: Exception | None = None):
        super().__init__(f"Failed to stop VM '{vm_name}'", cause)
        self.vm_name = vm_name


class VMDeleteError(VMError):
    """Raised when VM deletion fails."""

    def __init__(self, vm_name: str, cause: Exception | None = None):
        super().__init__(f"Failed to delete VM '{vm_name}'", cause)
        self.vm_name = vm_name


class VMTimeoutError(VMError):
    """Raised when VM operation times out."""

    def __init__(self, operation: str, timeout: int):
        super().__init__(
            f"VM operation '{operation}' timed out after {timeout} seconds"
        )
        self.operation = operation
        self.timeout = timeout
