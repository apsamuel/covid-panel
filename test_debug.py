"""
If python debugging is properly configured, executing the "Debug current file" task should step through this script
"""
import debugpy

print(
    "You will be immediately put into a breakpoint."
)
debugpy.breakpoint()

test_list = ["foo", "bar"]

test_dict = {"foo": "bar"}

TEST_STR = "foobar"

TEST_NUM = 10

print(TEST_STR * TEST_NUM)
