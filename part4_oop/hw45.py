from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class _BaseOrderPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]

        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class FIFOPolicy(_BaseOrderPolicy[K]):
    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)


@dataclass
class LRUPolicy(_BaseOrderPolicy[K]):
    def register_access(self, key: K) -> None:
        self.remove_key(key)
        self._order.append(key)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._order.append(key)

        current_count = self._key_counter.get(key, 0)
        self._key_counter[key] = current_count + 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        evictable_keys = self._order[: self.capacity]
        min_count = min(self._key_counter[key] for key in evictable_keys)

        for key in self._order:
            if self._key_counter[key] == min_count:
                return key

        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._key_counter.clear()
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)

        victim = self.policy.get_key_to_evict()

        if victim is not None:
            self.remove(victim)

    def get(self, key: K) -> V | None:
        value = self.storage.get(key)

        if value is not None:
            self.policy.register_access(key)

        return value

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self.__attr_name = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> Self | V:
        if instance is None:
            return self

        result = instance.cache.get(self.__attr_name)

        if result is None:
            result = self.func(instance)
            instance.cache.set(self.__attr_name, result)

        return result
