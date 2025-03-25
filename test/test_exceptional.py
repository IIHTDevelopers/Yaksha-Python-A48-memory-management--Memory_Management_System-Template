"""
Exceptional tests for Python Memory Management solution.
"""

import pytest
import sys
import gc
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


class TestExceptional:
    """Test class for error handling in the memory management solution."""

    def test_error_handling(self):
        """Test error handling in all memory management functions."""
        # 1. Test object_size with unusual objects
        # These should not raise exceptions
        object_size(lambda x: x)  # Function
        object_size(type)  # Type object
        object_size(object)  # Class
        object_size(Exception)  # Exception class
        object_size(object())  # Generic object
        
        # Test with recursive objects (potential for stack overflow)
        lst = []
        lst.append(lst)  # Self-referential list
        object_size(lst)  # Should handle this without error
        
        # 2. Test ObjectPool with problematic inputs
        # Invalid factory function
        with pytest.raises((TypeError, AttributeError)):
            pool = ObjectPool("not a function")
            obj = pool.get()
            
        # Factory that raises exception
        def failing_factory():
            raise ValueError("Factory failure")
            
        error_pool = ObjectPool(failing_factory)
        with pytest.raises(ValueError):
            obj = error_pool.get()
            
        # Factory that returns problematic objects
        def factory_returning_none():
            return None
            
        none_pool = ObjectPool(factory_returning_none)
        obj = none_pool.get()
        assert obj is None
        none_pool.release(obj)  # Should handle None properly
        
        # 3. Test releasing invalid objects to pool
        normal_pool = ObjectPool(lambda: {})
        
        # These should be handled gracefully (not crash)
        normal_pool.release(None)
        normal_pool.release(123)
        normal_pool.release("string")
        normal_pool.release(object())
        
        # Test with objects that might cause issues
        class Problematic:
            def __del__(self):
                # This could raise an exception during GC
                raise RuntimeError("Error in __del__")
                
        # Create and release a problematic object
        try:
            prob_obj = Problematic()
            normal_pool.release(prob_obj)
            del prob_obj
            gc.collect()
        except RuntimeError:
            # This might happen depending on Python's error handling in GC
            pass
        
        # 4. Test weakref with non-referenceable objects
        # These should raise TypeError
        with pytest.raises(TypeError):
            weakref.ref(42)
            
        with pytest.raises(TypeError):
            weakref.ref(True)
            
        with pytest.raises(TypeError):
            weakref.ref(None)
            
        # 5. Test circular references with problematic __del__ methods
        class ProblematicNode:
            def __init__(self, name):
                self.name = name
                self.neighbor = None
                self.data = [0] * 10000  # Add memory pressure
                
            def __del__(self):
                # Access neighbor during deletion which could cause issues
                try:
                    if hasattr(self, 'neighbor') and self.neighbor:
                        neighbor_name = self.neighbor.name
                except:
                    pass
        
        # Create circular reference with problematic nodes
        nodes = []
        for i in range(20):
            nodes.append(ProblematicNode(f"Node-{i}"))
            
        # Create circular references
        for i in range(20):
            nodes[i].neighbor = nodes[(i+1) % 20]
            
        # Remove references and collect - should not crash
        del nodes
        gc.collect()
        
        # 6. Test tracking during exceptions
        def function_with_complex_exception():
            # Create large objects
            objects = []
            for i in range(100):
                objects.append([0] * 10000)  # Create significant memory usage
                
            # Nested exception handling
            try:
                raise ValueError("Inner exception")
            except ValueError:
                # Trigger another exception that wraps the first
                try:
                    # Create more objects in exception handler
                    more_objects = [[i] * 1000 for i in range(100)]
                    objects.extend(more_objects)
                    
                    # Raise a different exception
                    raise RuntimeError("Outer exception")
                except RuntimeError:
                    # Handle but let some objects go out of scope
                    del more_objects
            
            # Let the function complete with error
            raise SystemError("Final exception")
            
        # Run tracking around complex exception handling
        before_count = len(gc.get_objects())
        
        try:
            function_with_complex_exception()
        except SystemError:
            pass
            
        # Force collection
        gc.collect()
        time.sleep(0.1)  # Give GC time to work
        after_count = len(gc.get_objects())
        
        # 7. Test with memory pressure and GC stress
        # Create and destroy many objects rapidly
        for _ in range(10):
            objects = []
            for i in range(1000):
                objects.append([0] * 1000)
            del objects
            gc.collect()
        
        # Verify we can still run our memory measurement functions
        before, after = track_objects_count()
        assert isinstance(before, int)
        assert isinstance(after, int)