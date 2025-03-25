"""
Python and Memory - Memory Management

This module demonstrates Python's memory management, including reference counting,
garbage collection, and techniques to prevent memory leaks.
"""

import gc
import sys
import time
import weakref


def track_objects_count():
    """
    Track the number of objects before and after garbage collection.
    
    Returns:
        Tuple with objects count before and after garbage collection
    """
    # Count objects before collection
    count_before = len(gc.get_objects())
    
    # Run garbage collection and get count after
    gc.collect()
    count_after = len(gc.get_objects())
    
    return count_before, count_after


def object_size(obj):
    """
    Measure the memory size of an object in bytes.
    
    Args:
        obj: Object to measure
        
    Returns:
        Size in bytes
    """
    return sys.getsizeof(obj)


def demonstrate_reference_counting():
    """
    Demonstrate Python's reference counting system.
    
    Returns:
        Dictionary with reference counts at different stages
    """
    class CountedObject:
        """Simple class to show object creation and deletion."""
        def __init__(self, name):
            self.name = name
            print(f"Object '{name}' created")
            
        def __del__(self):
            print(f"Object '{self.name}' destroyed")
    
    # Create object with one reference
    print("\nCreating object...")
    obj = CountedObject("test")
    
    # Create a second reference
    print("\nCreating second reference...")
    obj2 = obj
    
    # Delete first reference
    print("\nDeleting first reference...")
    del obj
    
    # Delete second reference
    print("\nDeleting second reference...")
    del obj2
    
    # Reference counts:
    # 1. After creation: 1 (obj)
    # 2. After second reference: 2 (obj and obj2)
    # 3. After deleting first: 1 (obj2)
    # 4. After deleting second: 0 (object is destroyed)
    
    return "Reference counting demonstration complete"


def create_circular_reference():
    """
    Demonstrate a circular reference which can cause memory leaks.
    
    Returns:
        Description of the created objects
    """
    class Node:
        def __init__(self, name):
            self.name = name
            self.neighbors = []
            print(f"Node '{name}' created")
            
        def __del__(self):
            print(f"Node '{self.name}' destroyed")
    
    # Create nodes
    print("\nCreating nodes with circular references...")
    nodes = [Node(f"Node-{i}") for i in range(3)]
    
    # Create circular references (each node points to the next)
    for i in range(3):
        nodes[i].neighbors.append(nodes[(i+1) % 3])
    
    # Remove our references to the nodes
    print("\nRemoving external references to nodes...")
    del nodes
    
    # Force garbage collection
    print("\nRunning garbage collection...")
    gc.collect()
    print("\nNodes with circular references aren't garbage collected!")
    
    return "Circular reference demonstration complete"


def fix_circular_reference():
    """
    Fix circular reference memory leak using weak references.
    
    Returns:
        Description of the created objects
    """
    class Node:
        def __init__(self, name):
            self.name = name
            self.neighbors = []
            print(f"Node '{name}' created")
            
        def __del__(self):
            print(f"Node '{self.name}' destroyed")
    
    # Create nodes
    print("\nCreating nodes with weak references...")
    nodes = [Node(f"Node-{i}") for i in range(3)]
    
    # Create circular references using weak references
    for i in range(3):
        nodes[i].neighbors.append(weakref.proxy(nodes[(i+1) % 3]))
    
    # Remove our references to the nodes
    print("\nRemoving external references to nodes...")
    del nodes
    
    # Force garbage collection
    print("\nRunning garbage collection...")
    gc.collect()
    print("\nNodes with weak references are properly garbage collected!")
    
    return "Weak reference demonstration complete"


def compare_data_structures():
    """
    Compare memory usage of different data structures.
    
    Returns:
        Dictionary with memory usage for common data structures
    """
    results = {}
    
    # Create data structures with 100,000 integers
    count = 100000
    
    # Measure list
    list_data = list(range(count))
    results["list"] = object_size(list_data)
    
    # Measure tuple
    tuple_data = tuple(range(count))
    results["tuple"] = object_size(tuple_data)
    
    # Measure set
    set_data = set(range(count))
    results["set"] = object_size(set_data)
    
    # Measure dictionary
    dict_data = {i: i for i in range(count)}
    results["dict"] = object_size(dict_data)
    
    # Print results
    print("\nMemory usage comparison:")
    for struct, memory in results.items():
        print(f"- {struct}: {memory / 1024:.2f} KB")
    
    return results


def demonstrate_generator_vs_list():
    """
    Compare memory usage between generators and lists.
    """
    count = 1000000
    
    # Measure memory for list
    print("\nCreating list of 1 million integers...")
    start_time = time.time()
    numbers_list = [i for i in range(count)]
    list_size = object_size(numbers_list)
    list_time = time.time() - start_time
    
    # Measure memory for generator (note: generators are lazy)
    print("\nCreating generator for 1 million integers...")
    start_time = time.time()
    numbers_gen = (i for i in range(count))
    gen_size = object_size(numbers_gen)
    gen_time = time.time() - start_time
    
    # Report results
    print(f"\nList: {list_size / 1024 / 1024:.2f} MB, created in {list_time:.4f}s")
    print(f"Generator: {gen_size / 1024:.2f} KB, created in {gen_time:.4f}s")
    print(f"Memory efficiency ratio: {list_size / gen_size:.0f}x")
    
    # Show efficiency when processing
    print("\nProcessing all values...")
    
    start_time = time.time()
    list_sum = sum(numbers_list)
    list_process_time = time.time() - start_time
    
    # Recreate generator since they can only be used once
    numbers_gen = (i for i in range(count))
    start_time = time.time()
    gen_sum = sum(numbers_gen)
    gen_process_time = time.time() - start_time
    
    print(f"List processing time: {list_process_time:.4f}s")
    print(f"Generator processing time: {gen_process_time:.4f}s")
    
    return "Generator vs List demonstration complete"


class ObjectPool:
    """Object pool for efficient reuse of expensive objects."""
    
    def __init__(self, factory_func, max_size=10):
        """
        Initialize the object pool.
        
        Args:
            factory_func: Function to create new objects
            max_size: Maximum number of objects in the pool
        """
        self.factory_func = factory_func
        self.max_size = max_size
        self.pool = []
        
    def get(self):
        """
        Get an object from the pool or create a new one.
        
        Returns:
            An object
        """
        if self.pool:
            return self.pool.pop()
        return self.factory_func()
        
    def release(self, obj):
        """
        Return an object to the pool if there's space.
        
        Args:
            obj: Object to return to the pool
        """
        if len(self.pool) < self.max_size:
            self.pool.append(obj)


def demonstrate_object_pooling():
    """
    Demonstrate how object pooling improves memory usage and performance.
    """
    # Create an expensive object factory function
    def create_expensive_object():
        # Simulate expensive creation
        time.sleep(0.001)  # 1ms delay
        return {"data": [0] * 1000}  # 1000-element list
    
    # Create a pool
    print("\nCreating object pool...")
    pool = ObjectPool(create_expensive_object, max_size=10)
    
    # Test with object pooling
    print("\nTesting with object pooling...")
    start_time = time.time()
    for _ in range(1000):
        obj = pool.get()
        # Use the object...
        pool.release(obj)
    pooled_time = time.time() - start_time
    
    # Test without object pooling
    print("\nTesting without object pooling...")
    start_time = time.time()
    for _ in range(1000):
        obj = create_expensive_object()
        # Use the object...
        # Object gets garbage collected
    unpooled_time = time.time() - start_time
    
    # Report results
    print(f"\nTime with object pooling: {pooled_time:.4f}s")
    print(f"Time without object pooling: {unpooled_time:.4f}s")
    print(f"Speed improvement: {unpooled_time / pooled_time:.2f}x")
    
    return "Object pooling demonstration complete"


def main():
    """
    Main function demonstrating Python's memory management features.
    """
    print("Python Memory Management Analysis")
    print("=================================")
    
    # Enable garbage collection debugging
    gc.enable()
    
    # 1. Reference Counting
    print("\n1. REFERENCE COUNTING DEMONSTRATION")
    print("---------------------------------")
    demonstrate_reference_counting()
    
    # 2. Circular References (Memory Leak)
    print("\n2. CIRCULAR REFERENCE DEMONSTRATION")
    print("---------------------------------")
    create_circular_reference()
    
    # 3. Fixing Circular References with Weak References
    print("\n3. WEAK REFERENCE DEMONSTRATION")
    print("-----------------------------")
    fix_circular_reference()
    
    # 4. Data Structure Memory Usage
    print("\n4. DATA STRUCTURE MEMORY COMPARISON")
    print("---------------------------------")
    compare_data_structures()
    
    # 5. Generator vs List Memory Usage
    print("\n5. GENERATOR VS LIST COMPARISON")
    print("-----------------------------")
    demonstrate_generator_vs_list()
    
    # 6. Object Pooling
    print("\n6. OBJECT POOLING DEMONSTRATION")
    print("-----------------------------")
    demonstrate_object_pooling()
    
    # 7. Garbage Collection Statistics
    print("\n7. GARBAGE COLLECTION STATISTICS")
    print("-----------------------------")
    before, after = track_objects_count()
    print(f"Objects before garbage collection: {before}")
    print(f"Objects after garbage collection: {after}")
    print(f"Objects cleaned up: {before - after}")
    
    print("\nMemory Management Analysis Complete")


if __name__ == "__main__":
    main()