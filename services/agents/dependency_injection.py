"""
Dependency Injection Framework for Agent Services

This module provides a lightweight dependency injection container
inspired by NestJS but tailored for Python agent services.

Features:
- Constructor injection with type hints
- Singleton and transient lifecycle management
- Factory function support
- Circular dependency detection
- Service registration decorators
"""

import inspect
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Callable,
    get_type_hints,
    get_origin,
    get_args,
)
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime management strategies."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceDescriptor:
    """Describes how a service should be instantiated."""

    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    instance: Optional[Any] = None


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""

    pass


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""

    pass


class DependencyInjectionContainer:
    """
    Lightweight dependency injection container.

    Provides service registration, resolution, and lifecycle management
    for agent services following SOLID principles.
    """

    def __init__(self) -> None:
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._resolution_stack: List[Type] = []
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}

    def register_singleton(
        self, service_type: Type[T], implementation_type: Optional[Type[T]] = None
    ) -> "DependencyInjectionContainer":
        """Register a service as singleton."""
        return self._register_service(service_type, implementation_type, ServiceLifetime.SINGLETON)

    def register_transient(
        self, service_type: Type[T], implementation_type: Optional[Type[T]] = None
    ) -> "DependencyInjectionContainer":
        """Register a service as transient (new instance each time)."""
        return self._register_service(service_type, implementation_type, ServiceLifetime.TRANSIENT)

    def register_scoped(
        self, service_type: Type[T], implementation_type: Optional[Type[T]] = None
    ) -> "DependencyInjectionContainer":
        """Register a service as scoped (per scope/request)."""
        return self._register_service(service_type, implementation_type, ServiceLifetime.SCOPED)

    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> "DependencyInjectionContainer":
        """Register a service with a factory function."""
        descriptor = ServiceDescriptor(
            service_type=service_type, factory=factory, lifetime=lifetime
        )
        self._services[service_type] = descriptor
        return self

    def register_instance(
        self, service_type: Type[T], instance: T
    ) -> "DependencyInjectionContainer":
        """Register a pre-created instance."""
        descriptor = ServiceDescriptor(
            service_type=service_type, instance=instance, lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        return self

    def _register_service(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]],
        lifetime: ServiceLifetime,
    ) -> "DependencyInjectionContainer":
        """Internal service registration method."""
        impl_type = implementation_type or service_type

        descriptor = ServiceDescriptor(
            service_type=service_type, implementation_type=impl_type, lifetime=lifetime
        )
        self._services[service_type] = descriptor
        return self

    def resolve(self, service_type: Type[T], scope_id: Optional[str] = None) -> T:
        """
        Resolve a service instance with its dependencies.

        Args:
            service_type: The type of service to resolve
            scope_id: Optional scope identifier for scoped services

        Returns:
            Configured service instance

        Raises:
            ServiceNotFoundError: If service is not registered
            CircularDependencyError: If circular dependencies detected
        """
        if service_type not in self._services:
            raise ServiceNotFoundError(f"Service {service_type.__name__} is not registered")

        descriptor = self._services[service_type]

        # Check for circular dependencies
        if service_type in self._resolution_stack:
            cycle = " -> ".join(
                t.__name__
                for t in self._resolution_stack[self._resolution_stack.index(service_type) :]
            )
            raise CircularDependencyError(
                f"Circular dependency detected: {cycle} -> {service_type.__name__}"
            )

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is not None:
                return descriptor.instance

            instance = self._create_instance(descriptor, scope_id)
            descriptor.instance = instance
            return instance

        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if not scope_id:
                scope_id = "default"

            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}

            scoped_cache = self._scoped_instances[scope_id]
            if service_type in scoped_cache:
                return scoped_cache[service_type]

            instance = self._create_instance(descriptor, scope_id)
            scoped_cache[service_type] = instance
            return instance

        else:  # TRANSIENT
            return self._create_instance(descriptor, scope_id)

    def _create_instance(self, descriptor: ServiceDescriptor, scope_id: Optional[str]) -> Any:
        """Create a new service instance."""
        self._resolution_stack.append(descriptor.service_type)

        try:
            if descriptor.instance is not None:
                return descriptor.instance

            if descriptor.factory:
                return descriptor.factory()

            if descriptor.implementation_type:
                return self._create_with_constructor_injection(
                    descriptor.implementation_type, scope_id
                )

            # Default constructor
            return descriptor.service_type()

        finally:
            self._resolution_stack.pop()

    def _create_with_constructor_injection(self, impl_type: Type, scope_id: Optional[str]) -> Any:
        """Create instance with constructor dependency injection."""
        # Get constructor signature
        constructor = impl_type.__init__
        signature = inspect.signature(constructor)
        type_hints = get_type_hints(constructor)

        # Build constructor arguments
        kwargs = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name)
            if param_type is None:
                # No type hint, check if has default value
                if param.default != inspect.Parameter.empty:
                    continue
                else:
                    raise ServiceNotFoundError(
                        f"Parameter '{param_name}' in {impl_type.__name__} has no type hint and no default value"
                    )

            # Handle Optional types
            if self._is_optional_type(param_type):
                actual_type = self._get_optional_inner_type(param_type)
                if actual_type and actual_type in self._services:
                    kwargs[param_name] = self.resolve(actual_type, scope_id)
                else:
                    kwargs[param_name] = None
            else:
                # Required dependency
                kwargs[param_name] = self.resolve(param_type, scope_id)

        return impl_type(**kwargs)

    def _is_optional_type(self, type_hint: Type) -> bool:
        """Check if type hint represents Optional[T]."""
        origin = get_origin(type_hint)
        if origin is not type(None):  # Union type
            args = get_args(type_hint)
            return len(args) == 2 and type(None) in args
        return False

    def _get_optional_inner_type(self, type_hint: Type) -> Optional[Type]:
        """Extract T from Optional[T]."""
        args = get_args(type_hint)
        for arg in args:
            if arg is not type(None):
                return arg
        return None

    def create_scope(self, scope_id: str) -> "ServiceScope":
        """Create a new service scope for scoped services."""
        return ServiceScope(self, scope_id)

    def dispose_scope(self, scope_id: str) -> None:
        """Dispose of a service scope and its instances."""
        if scope_id in self._scoped_instances:
            scoped_instances = self._scoped_instances[scope_id]

            # Call dispose on instances that support it
            for instance in scoped_instances.values():
                if hasattr(instance, "dispose"):
                    try:
                        instance.dispose()
                    except Exception:
                        pass  # Ignore disposal errors

            del self._scoped_instances[scope_id]

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services

    def get_registered_services(self) -> List[Type]:
        """Get list of all registered service types."""
        return list(self._services.keys())


class ServiceScope:
    """
    Service scope for managing scoped service lifetimes.

    Use with context manager for automatic disposal:
    with container.create_scope("request_123") as scope:
        service = scope.resolve(MyService)
    """

    def __init__(self, container: DependencyInjectionContainer, scope_id: str) -> None:
        self.container = container
        self.scope_id = scope_id

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service within this scope."""
        return self.container.resolve(service_type, self.scope_id)

    def __enter__(self) -> "ServiceScope":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.dispose_scope(self.scope_id)


# Decorator for service registration
def injectable(
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON, register_as: Optional[Type] = None
):
    """
    Decorator to mark a class as injectable service.

    Args:
        lifetime: Service lifetime strategy
        register_as: Interface/base class to register as (defaults to decorated class)

    Example:
        @injectable(ServiceLifetime.SINGLETON)
        class UserService:
            def __init__(self, repository: UserRepository):
                self.repository = repository
    """

    def decorator(cls):
        cls._di_lifetime = lifetime
        cls._di_register_as = register_as or cls
        return cls

    return decorator


# Global container instance
_global_container: Optional[DependencyInjectionContainer] = None


def get_container() -> DependencyInjectionContainer:
    """Get the global dependency injection container."""
    global _global_container
    if _global_container is None:
        _global_container = DependencyInjectionContainer()
    return _global_container


def configure_services(configuration_func: Callable[[DependencyInjectionContainer], None]) -> None:
    """Configure services in the global container."""
    container = get_container()
    configuration_func(container)


def auto_register_services(*modules) -> None:
    """
    Automatically register services marked with @injectable decorator.

    Args:
        *modules: Modules to scan for injectable services
    """
    container = get_container()

    for module in modules:
        for name in dir(module):
            obj = getattr(module, name)

            if (
                inspect.isclass(obj)
                and hasattr(obj, "_di_lifetime")
                and hasattr(obj, "_di_register_as")
            ):
                lifetime = obj._di_lifetime
                register_as = obj._di_register_as

                if lifetime == ServiceLifetime.SINGLETON:
                    container.register_singleton(register_as, obj)
                elif lifetime == ServiceLifetime.TRANSIENT:
                    container.register_transient(register_as, obj)
                elif lifetime == ServiceLifetime.SCOPED:
                    container.register_scoped(register_as, obj)


# Example usage and testing
if __name__ == "__main__":
    # Example service classes
    class IUserRepository(ABC):
        @abstractmethod
        def get_user(self, user_id: str) -> str:
            pass

    @injectable(ServiceLifetime.SINGLETON, IUserRepository)
    class UserRepository(IUserRepository):
        def get_user(self, user_id: str) -> str:
            return f"User {user_id}"

    @injectable(ServiceLifetime.TRANSIENT)
    class UserService:
        def __init__(self, repository: IUserRepository) -> None:
            self.repository = repository

        def get_user_info(self, user_id: str) -> str:
            return f"Info: {self.repository.get_user(user_id)}"

    # Configure container
    def configure(container: DependencyInjectionContainer) -> None:
        container.register_singleton(IUserRepository, UserRepository)
        container.register_transient(UserService)

    configure_services(configure)

    # Test resolution
    container = get_container()

    user_service1 = container.resolve(UserService)
    user_service2 = container.resolve(UserService)

    print(f"Service 1: {user_service1.get_user_info('123')}")
    print(f"Service 2: {user_service2.get_user_info('456')}")
    print(f"Same repository instance: {user_service1.repository is user_service2.repository}")
    print(f"Different service instances: {user_service1 is not user_service2}")
