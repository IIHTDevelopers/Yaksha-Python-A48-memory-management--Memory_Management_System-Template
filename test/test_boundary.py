"""
Boundary tests for Python Memory Management solution.
"""

import pytest
import gc
import sys
import time
import weakref
from memory_management import (
    track_objects_count,
    object_size,
    demonstrate_reference_counting,
    create_circular_reference,
    fix_circular_reference,
    compare_data_structures,
    demonstrate_generator_vs_list,
    ObjectPool
)


class TestBoundary:
    """Test class for boundary cases of the memory management solution."""

    def test_boundary_cases(self):
        """Test various boundary cases in the memory management implementation."""
        # Test object_size with extreme cases
        
        # 1. Empty/minimal objects
        assert object_size(None) > 0
        assert object_size(True) > 0
        assert object_size(0) > 0
        assert object_size("") > 0
        assert object_size([]) > 0
        assert object_size({}) > 0
        assert object_size(set()) > 0
        assert object_size(tuple()) > 0
        
        # 2. Very large objects
        large_list = [0] * 1000000  # 1 million zeros
        large_list_size = object_size(large_list)
        assert large_list_size > 1000000  # Should be at least 1MB
        
        large_dict = {i: i*2 for i in range(100000)}
        large_dict_size = object_size(large_dict)
        assert large_dict_size > 1000000
        
        # 3. Nested structures
        nested_list = []
        current = nested_list
        for i in range(1000):  # Create deeply nested list
            current.append([])
            current = current[0]
        nested_size = object_size(nested_list)
        # Note: sys.getsizeof() only measures the direct memory of the object, not recursive contents
        assert nested_size > 80  # Just check that it's a reasonable size for a list
        
        # 4. Object pool with extreme values
        def simple_factory():
            return {}
            
        # Pool with zero capacity
        zero_pool = ObjectPool(simple_factory, max_size=0)
        for _ in range(100):  # Get many objects
            obj = zero_pool.get()
            zero_pool.release(obj)  # Should not store any
        assert len(zero_pool.pool) == 0
        
        # Pool with very large capacity
        large_pool = ObjectPool(simple_factory, max_size=1000000)
        test_objs = []
        for _ in range(1000):  # Create 1000 objects
            obj = large_pool.get()
            test_objs.append(obj)
        
        # Release all objects
        for obj in test_objs:
            large_pool.release(obj)
        assert len(large_pool.pool) == 1000  # All should be stored
        
        # 5. Circular references with deep nesting and complex structure
        class Node:
            def __init__(self, value):
                self.value = value
                self.left = None
                self.right = None
                self.parent = None
                # Add significant memory usage
                self.data = [0] * 1000
                
        # Create a binary tree with circular references (child->parent)
        def build_tree(depth, parent=None):
            if depth <= 0:
                return None
            node = Node(depth)
            node.parent = parent  # circular reference
            node.left = build_tree(depth-1, node)
            node.right = build_tree(depth-1, node)
            return node
            
        # Create tree with significant depth
        root = build_tree(8)  # 2^8-1 = 255 nodes
        
        # Count objects before
        gc.collect()
        count_before = len(gc.get_objects())
        
        # Remove reference to root
        del root
        gc.collect()
        time.sleep(0.2)  # Give GC time for complex structures
        
        # Count after - circular references may prevent cleanup
        count_after = len(gc.get_objects())
        
        # 6. Test weak references with edge cases
        class RefTarget:
            def __init__(self, name):
                self.name = name
                
        # Create object and weak reference
        obj = RefTarget("test")
        ref = weakref.ref(obj)
        assert ref() is obj
        
        # Delete and recreate with same memory location (edge case)
        obj_id = id(obj)
        del obj
        gc.collect()
        
        # Reference should now be dead
        assert ref() is None
        
        # Try to create circular weak references
        a = RefTarget("a")
        b = RefTarget("b")
        a.ref = weakref.ref(b)
        b.ref = weakref.ref(a)
        
        # Delete both objects
        del a, b
        gc.collect()
        # Both should be collected (no memory leak)
        
        # 7. Test generator with very large range
        try:
            # Create generator for huge range
            huge_gen = (i for i in range(10**10))
            gen_size = object_size(huge_gen)
            
            # Generator should be small regardless of range
            assert gen_size < 1000
            
            # Access first few elements
            for i, val in enumerate(huge_gen):
                if i >= 10:
                    break
        except MemoryError:
            # Skip if we actually run out of memory
            pass
        
        # Clean up to avoid affecting other tests
        gc.collect()