import os

print("Current folder:")
print(os.getcwd())

print("\nFiles:")
for f in os.listdir():
    print(f)