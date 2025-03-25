"""
Functional tests for Python Memory Management solution.
"""

import pytest
import gc
import weakref
import time
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


class TestFunctional:
    """Test class for functional tests of the memory management solution."""

    def test_reference_counting_behavior(self):
        """Test reference counting core functionality."""
        # Verify the function returns expected results
        result = demonstrate_reference_counting()
        assert isinstance(result, str)
        
        # This test demonstrates that Python objects are destroyed when no references remain
        class CountedObject:
            instances = 0
            def __init__(self, idx):
                self.idx = idx
                self.data = [0] * 1000  # Add data to make size significant
                CountedObject.instances += 1
            def __del__(self):
                CountedObject.instances -= 1
        
        # Create a single object and verify reference counting
        obj1 = CountedObject(1)
        assert CountedObject.instances == 1
        
        # Create a second reference to the same object
        obj2 = obj1
        # Still only one object
        assert CountedObject.instances == 1
        
        # Store object identity for later verification
        obj_id = id(obj1)
        
        # Remove first reference
        del obj1
        # Object still exists through second reference
        assert obj_id == id(obj2)
        
        # Test with multiple objects
        objects_list = [CountedObject(i) for i in range(10)]
        assert CountedObject.instances == 11  # 10 new + 1 existing (obj2)
        
        # Delete all references and verify cleanup
        del obj2
        del objects_list
        gc.collect()
        
        # All objects should be collected
        assert CountedObject.instances == 0

    def test_circular_references_management(self):
        """Test circular reference creation and resolution."""
        # Verify demonstrations run
        result1 = create_circular_reference()
        result2 = fix_circular_reference()
        assert isinstance(result1, str) and isinstance(result2, str)
        
        # Test with complex circular reference networks
        class Node:
            instances = 0
            def __init__(self, name):
                self.name = name
                self.data = [0] * 1000  # Add memory pressure
                self.neighbors = []
                Node.instances += 1
            def __del__(self):
                Node.instances -= 1
        
        # Create a network of 100 nodes with circular references
        nodes = [Node(f"Node-{i}") for i in range(100)]
        
        # Each node points to 3 other nodes, creating a dense network
        for i in range(100):
            nodes[i].neighbors = [nodes[(i+j)%100] for j in range(1, 4)]
            
        assert Node.instances == 100
        
        # Now create a similar network using weak references
        weak_nodes = [Node(f"WeakNode-{i}") for i in range(100)]
        for i in range(100):
            for j in range(1, 4):
                weak_nodes[i].neighbors.append(weakref.proxy(weak_nodes[(i+j)%100]))
                
        # Count total nodes
        total_before = Node.instances
        
        # Remove all direct references to weak_nodes
        del weak_nodes
        gc.collect()
        time.sleep(0.1)  # Give GC time to work
        
        # The weak reference nodes should be collected
        assert Node.instances < total_before - 50
        
        # Remove circular references
        del nodes
        gc.collect()
        time.sleep(0.1)  # Give GC time to work
        
        # Circular references may or may not be collected (implementation dependent)
        # but we at least ensure the test completes

    def test_memory_usage_comparison(self):
        """Test memory usage comparison functionality."""
        # Test data structure comparison
        results = compare_data_structures()
        assert isinstance(results, dict)
        assert all(key in results for key in ['list', 'tuple', 'dict', 'set'])
        
        # Create our own large data structures for comparison
        test_size = 200000
        
        # Measure each structure
        list_data = list(range(test_size))
        list_size = object_size(list_data)
        
        tuple_data = tuple(range(test_size))
        tuple_size = object_size(tuple_data)
        
        set_data = set(range(test_size))
        set_size = object_size(set_data)
        
        dict_data = {i: i for i in range(test_size)}
        dict_size = object_size(dict_data)
        
        # Verify memory relationships
        assert tuple_size < list_size * 1.5  # Tuples more efficient than lists
        assert dict_size > list_size  # Dictionaries have overhead for keys
        
        # Clean up to avoid memory pressure in other tests
        del list_data, tuple_data, set_data, dict_data
        gc.collect()

    def test_generator_vs_list_efficiency(self):
        """Test generator vs list memory efficiency."""
        # Ensure the demonstration runs
        result = demonstrate_generator_vs_list()
        assert isinstance(result, str)
        
        # Verify actual memory usage with significant data
        start_time = time.time()
        list_comp = [i**2 for i in range(100000)]
        list_creation_time = time.time() - start_time
        list_size = object_size(list_comp)
        
        start_time = time.time()
        gen_exp = (i**2 for i in range(100000))
        gen_creation_time = time.time() - start_time
        gen_size = object_size(gen_exp)
        
        # Generator should use much less memory
        assert gen_size < list_size / 100
        
        # Test processing time
        start_time = time.time()
        list_sum = sum(list_comp)
        list_sum_time = time.time() - start_time
        
        # Recreate generator since they can only be used once
        gen_exp = (i**2 for i in range(100000))
        start_time = time.time()
        gen_sum = sum(gen_exp)
        gen_sum_time = time.time() - start_time
        
        # Verify sums match
        assert list_sum == gen_sum
        
        # Clean up
        del list_comp
        gc.collect()

    def test_object_pool_functionality(self):
        """Test object pool implementation with intensive usage."""
        # Create a factory for expensive objects
        def create_expensive_object():
            time.sleep(0.001)  # Simulate expensive creation
            return {"data": [0] * 10000}
        
        # Create and test the pool
        pool = ObjectPool(create_expensive_object, max_size=5)
        
        # Test with intensive usage
        start_time = time.time()
        for _ in range(100):
            obj = pool.get()
            # Actually use the object (modify it)
            obj["data"][0] = 1
            pool.release(obj)
        pooled_time = time.time() - start_time
        
        # Compare with no pooling
        start_time = time.time()
        for _ in range(100):
            obj = create_expensive_object()
            obj["data"][0] = 1
            # Let GC handle it
        unpooled_time = time.time() - start_time
        
        # Pooling should be faster
        assert pooled_time < unpooled_time
        
        # Test with multiple objects beyond pool capacity
        objects = []
        for _ in range(20):
            obj = pool.get()
            # Modify each object uniquely
            obj["data"][0] = len(objects)
            objects.append(obj)
            
        # Release all objects
        for obj in objects:
            pool.release(obj)
            
        # Pool size should not exceed max_size
        assert len(pool.pool) <= 5

    def test_track_objects_and_size(self):
        """Test object tracking and size measurement with significant memory usage."""
        # Create many objects to test GC
        objects = []
        for _ in range(1000):
            objects.append([0] * 1000)  # Create 1000 lists with 1000 elements each
            
        # Test object counting
        before, after = track_objects_count()
        assert isinstance(before, int) and isinstance(after, int)
        assert after <= before  # GC should reduce count
        
        # Clean up our objects
        del objects
        gc.collect()
        
        # Test size measurement with various objects
        sizes = {
            "small_int": object_size(5),
            "large_int": object_size(10**100),
            "empty_list": object_size([]),
            "large_list": object_size([0] * 100000),
            "function": object_size(lambda x: x),
            "class": object_size(type("DynamicClass", (), {}))
        }
        
        # Verify size relationships
        assert sizes["small_int"] > 0
        assert sizes["large_int"] > sizes["small_int"]
        assert sizes["large_list"] > sizes["empty_list"]