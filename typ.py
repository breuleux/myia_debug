from dataclasses import dataclass
from myia.dtype import Bool, Int, Float, List, Array, pytype_to_myiatype, \
    Tuple, JTagged
from myia.abstract import ANYTHING as ANY  # noqa: F401

B = Bool

i16 = Int[16]
i32 = Int[32]
i64 = Int[64]

f16 = Float[16]
f32 = Float[32]
f64 = Float[64]

li16 = List[Int[16]]
li32 = List[Int[32]]
li64 = List[Int[64]]

lf16 = List[Float[16]]
lf32 = List[Float[32]]
lf64 = List[Float[64]]

ai16 = Array[Int[16]]
ai32 = Array[Int[32]]
ai64 = Array[Int[64]]

af16 = Array[Float[16]]
af32 = Array[Float[32]]
af64 = Array[Float[64]]


@dataclass(frozen=True)
class Point:
    x: i64
    y: i64

    def abs(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __add__(self, other):
        return Point(self.x * other.x, self.y * other.y)


pt = pytype_to_myiatype(Point)
lpt = List[pt]
