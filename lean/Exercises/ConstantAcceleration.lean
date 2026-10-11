import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
# Exercises: constant acceleration

Replace each `sorry` with a proof, then check the file from the `lean/`
directory of the repository:

    lake env lean Exercises/ConstantAcceleration.lean

Lean reports "declaration uses 'sorry'" for a theorem you have not proved yet
and nothing for one you have. The model is that of the kinematics lesson: the
position and the velocity at time `t` are given by the two formulas, taken as
hypotheses. The checked solutions are in
`PhysicsByConstruction/Exercises/ConstantAcceleration.lean`.
-/

namespace PhysicsByConstruction.Exercises

-- ANCHOR: displacement_from_speeds
/-- With a non-zero constant acceleration `a`, the distance covered is the
change of the squared speed divided by `2 a`. -/
theorem displacement_from_speeds
    (x₀ v₀ a t x v : ℝ) (ha : a ≠ 0)
    (hx : x = x₀ + v₀ * t + a * t ^ 2 / 2)
    (hv : v = v₀ + a * t) :
    x - x₀ = (v ^ 2 - v₀ ^ 2) / (2 * a) := by
  sorry
-- ANCHOR_END: displacement_from_speeds

-- ANCHOR: time_from_speeds
/-- With a non-zero constant acceleration `a`, the time taken is the change
of speed divided by `a`. -/
theorem time_from_speeds
    (v₀ a t v : ℝ) (ha : a ≠ 0)
    (hv : v = v₀ + a * t) :
    t = (v - v₀) / a := by
  sorry
-- ANCHOR_END: time_from_speeds

end PhysicsByConstruction.Exercises
