# import time
# from functools import wraps

# def timeneed(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
        
#         execution_time = end_time - start_time
#         print(f"time_taken : {execution_time:.6f} seconds")
#         return result
#     return wrapper

# @timeneed
# def simple_sleep_test(sleep_duration=1.5):
#     time.sleep(sleep_duration)

# if __name__ == "__main__":
#     simple_sleep_test(1.5)


# def say_hello(name):
#     return f"Hello, {name}"

# def yo(name):
#     return f"Yo {name}, together we shall conquer the world"

# def greet_chirag(greeter_func):
#     return greeter_func("chirag")

# print(greet_chirag(say_hello))
# print(greet_chirag(yo))

# def decorator(func):
#     def wrapper():
#         print("someyhing is happening before the function is called")
#         func()
#         print("something is happening after the function is called")
#         return wrapper

# def say_hello():
#     print("hello")

# say_hello = decorator(say_hello)
# say_hello()


# def decorator(func):
#     def wrapper():
#         print("something is happening before the function is called")
#         func()
#         print("something is happening after the function is called")
#     return wrapper

# def say_hello():
#     print("hello")

# say_hello = decorator(say_hello)

# say_hello()


# from datetime import datetime

# def not_during_the_night(func):
#     def wrapper():
#         if 7 <= datetime.now().hour <22:
#             func()
#             func()

#         else:
#             pass 
#     return wrapper
    

# @not_during_the_night
# def say_wee():
#     print("wakey wakey")


# say_wee()


# def do_twice(func):
#     def wrapper_do_twice( *args, **kwargs):
#         func(*args, **kwargs)
#         func(*args,**kwargs)
#     def wrapper_do_twice():
#         func()
#         func()
#     return wrapper_do_twice
# @do_twice
# def say_whee():
#     print("Whee!")

# from decorator import do_twice 
# def greet(name:str)->str:
#     print(f"Hello {name}")  
# say_whee()
# greet("Chirag")


def do_twice(func):
    def wrapper_do_twice(*args, **kwargs):
        # This one handles functions with OR without arguments
        func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper_do_twice

@do_twice
def say_whee():
    print("Whee!")

@do_twice
def greet(name: str):
    print(f"Hello {name}")

# Now both will work!
say_whee()
greet("Chirag")
