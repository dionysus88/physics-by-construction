import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
# Exercises: an impulse between two particles

Replace the `sorry` with a proof, then check the file from the `lean/`
directory of the repository:

    lake env lean Exercises/Impulse.lean

The checked solution is in `PhysicsByConstruction/Exercises/Impulse.lean`.
-/

namespace PhysicsByConstruction.Exercises

-- ANCHOR: impulse_momentum
/-- Two particles on a line exchange an impulse `J`: the first loses it, the
second gains it. Their total momentum is the same before and after. -/
theorem impulse_momentum
    (m₁ m₂ v₁ v₂ v₁' v₂' J : ℝ) (hm₁ : m₁ ≠ 0) (hm₂ : m₂ ≠ 0)
    (h₁ : v₁' = v₁ - J / m₁)
    (h₂ : v₂' = v₂ + J / m₂) :
    m₁ * v₁' + m₂ * v₂' = m₁ * v₁ + m₂ * v₂ := by
  sorry
-- ANCHOR_END: impulse_momentum

end PhysicsByConstruction.Exercises
