import queue
import threading

# Dictionary to store object pools
pools = {}

# Lock for thread-safe access to the `pools` dictionary
lock = threading.Lock()

def get_threadsafe_object(bucket_name, object_generator, obj_gen_args = (), obj_gen_kwargs = {}):
    """
    Retrieves an object from the resource pool associated with the specified bucket name.
    If no object is available, a new object is created using the provided object_generator function.

    :param bucket_name: The name of the bucket associated with the resource pool.
    :param object_generator: A function that generates a new object if the pool is empty.
    :param obj_gen_args: args for the object generator.
    :param obj_gen_kwargs: kwargs for the object generator.
    :return: The retrieved or newly created object.
    """
    with lock:
        # Check if the pool for the bucket exists, and create it if not
        if bucket_name not in pools:
            pools[bucket_name] = queue.Queue()

    try:
        # Attempt to retrieve an object from the pool with a timeout of 1 second
        obj = pools[bucket_name].get(timeout=1)
    except queue.Empty:
        # If the pool is empty, generate a new object using the object_generator function
        obj = object_generator(*obj_gen_args, **obj_gen_kwargs)

    return obj

def release_threadsafe_object(bucket_name, obj):
    """
    Releases an object back to the resource pool associated with the specified bucket name.

    :param bucket_name: The name of the bucket associated with the resource pool.
    :param obj: The object to be released back to the pool.
    """
    with lock:
        # Check if the pool for the bucket exists, and create it if not
        if bucket_name not in pools:
            pools[bucket_name] = queue.Queue()

        # Add the released object back to the pool
        pools[bucket_name].put(obj)