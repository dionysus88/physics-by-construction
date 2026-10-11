import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
# Exercises: constant acceleration (solutions)

The checked solutions of `lean/Exercises/ConstantAcceleration.lean`. The
statements are the same text as in the stubs, which
`scripts/check-lean.sh` verifies; only the proofs differ. The model is that
of `PhysicsByConstruction.Mechanics.Kinematics`: the position and the velocity
at time `t` are given by the two formulas, taken as hypotheses.
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
  subst hx hv
  field_simp
  ring
-- ANCHOR_END: displacement_from_speeds

-- ANCHOR: time_from_speeds
/-- With a non-zero constant acceleration `a`, the time taken is the change
of speed divided by `a`. -/
theorem time_from_speeds
    (v₀ a t v : ℝ) (ha : a ≠ 0)
    (hv : v = v₀ + a * t) :
    t = (v - v₀) / a := by
  subst hv
  field_simp
  ring
-- ANCHOR_END: time_from_speeds

end PhysicsByConstruction.Exercises
