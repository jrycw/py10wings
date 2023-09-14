# 13
import types

# old
none_type1 = type(None)

# new
none_type2 = types.NoneType

print(none_type1 is none_type2)  # True
