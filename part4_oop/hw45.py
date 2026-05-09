from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

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
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

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
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

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
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _last_new_key: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        is_new_key = key not in self._key_counter
        self._key_counter[key] = self._key_counter.get(key, 0) + 1
        if is_new_key:
            self._last_new_key = key

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        candidate_counters = self._get_candidate_counters()
        if not candidate_counters:
            return self._last_new_key
        return min(candidate_counters, key=candidate_counters.__getitem__)

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        if self._last_new_key == key or len(self._key_counter) <= self.capacity:
            self._last_new_key = None

    def clear(self) -> None:
        self._key_counter.clear()
        self._last_new_key = None

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0

    def _get_candidate_counters(self) -> dict[K, int]:
        if self._last_new_key is None:
            return self._key_counter
        return {
            counter_key: counter_value
            for counter_key, counter_value in self._key_counter.items()
            if counter_key != self._last_new_key
        }


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)
        self._evict_if_needed()

    def get(self, key: K) -> V | None:
        if not self.storage.exists(key):
            return None
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()

    def _evict_if_needed(self) -> None:
        evict_key = self.policy.get_key_to_evict()
        if evict_key is not None:
            self.storage.remove(evict_key)
            self.policy.remove_key(evict_key)


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func
        self._cache_key: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self._cache_key = f"{owner.__module__}.{owner.__qualname__}.{name}"

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]
        cache_key = self._cache_key
        if cache_key is None:
            cache_key = self._func.__qualname__
        cached: V | None = instance.cache.get(cache_key)
        if cached is not None:
            return cached
        result: V = self._func(instance)
        instance.cache.set(cache_key, result)
        return result
