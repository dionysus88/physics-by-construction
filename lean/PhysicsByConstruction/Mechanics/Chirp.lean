import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Inv

/-!
# The Newtonian-order chirp of two bodies on a circular orbit

The gravitational-wave strain lab models two point masses `m₁` and `m₂` on a
circular orbit of separation `a`. This module proves exact consequences of the
model, never of a measurement and never of the Python program:

* the orbit shrinks at the rate `da/dt = -(64/5) G³ m₁ m₂ M / (c⁵ a³)` when its
  energy `-G m₁ m₂ / (2a)` falls at the quadrupole power;
* with Kepler's third law, `(da/dt)` fixes the rate of change of the orbital
  angular frequency `ω = π f`, and that rate obeys `(ω')³ = (96/5)³ (G𝓜/c³)⁵ ω¹¹`
  with the chirp mass `𝓜`, where `𝓜⁵ = (m₁ m₂)³ / M`;
* the relation can be inverted: a frequency and its rate fix the chirp mass;
* a local countdown: where the law holds near an instant `t`, the time
  `τ = 3 ω / (8 ω')` has derivative `-1` at `t`, so it falls at the rate one
  there. That `τ` reaches the divergence, or is the time left to coalescence,
  is not established here.

Two things are assumptions, and they are hypotheses of the theorems. The power
radiated, `P = (32/5) G⁴ m₁² m₂² M / (c⁵ a⁵)`, is the quadrupole formula of
general relativity: it is an input, not derived here. The orbit stays
circular, so that Kepler's third law holds at every instant. Powers are
integers (the chirp mass is defined by its fifth power, the rate by its cube),
so no fractional power of a real number enters.
-/

namespace PhysicsByConstruction.Mechanics

-- ANCHOR: orbitEnergy
/-- The energy of a circular orbit of separation `a`: `-G m₁ m₂ / (2 a)`. -/
noncomputable def orbitEnergy (G m₁ m₂ a : ℝ) : ℝ :=
  -(G * m₁ * m₂) / (2 * a)

/-- The power of the quadrupole formula radiated by a circular orbit of
separation `a`, `(32/5) G⁴ m₁² m₂² (m₁ + m₂) / (c⁵ a⁵)`. An assumption of the
model, taken from general relativity. -/
noncomputable def quadrupolePower (G c m₁ m₂ a : ℝ) : ℝ :=
  32 / 5 * G ^ 4 * m₁ ^ 2 * m₂ ^ 2 * (m₁ + m₂) / (c ^ 5 * a ^ 5)
-- ANCHOR_END: orbitEnergy

-- ANCHOR: shrink_rate_of_energy_loss
/-- **The orbit shrinks at the rate the energy loss fixes.** If the separation
`a` of a circular orbit has the derivative `a'` at `t`, and the energy of the
orbit has the derivative `-P` there (`hloss`, the loss at the quadrupole
power), then `a' = -(64/5) G³ m₁ m₂ (m₁ + m₂) / (c⁵ a³)`. -/
theorem shrink_rate_of_energy_loss
    (G c m₁ m₂ : ℝ) (a : ℝ → ℝ) (a' t : ℝ)
    (hG : 0 < G) (hc : 0 < c) (hm₁ : 0 < m₁) (hm₂ : 0 < m₂) (ha0 : 0 < a t)
    (ha : HasDerivAt a a' t)
    (hloss : HasDerivAt (fun s => orbitEnergy G m₁ m₂ (a s))
      (-quadrupolePower G c m₁ m₂ (a t)) t) :
    a' = -(64 / 5) * G ^ 3 * m₁ * m₂ * (m₁ + m₂) / (c ^ 5 * a t ^ 3) := by
  have hne : a t ≠ 0 := ha0.ne'
  have h1 : HasDerivAt (fun s => 2 * a s) (2 * a') t := ha.const_mul 2
  have h2 : HasDerivAt (fun s => (2 * a s)⁻¹) (-(2 * a') / (2 * a t) ^ 2) t :=
    h1.inv (by positivity)
  have h3 := h2.const_mul (-(G * m₁ * m₂))
  have h4 : HasDerivAt (fun s => orbitEnergy G m₁ m₂ (a s))
      (-(G * m₁ * m₂) * (-(2 * a') / (2 * a t) ^ 2)) t := by
    refine h3.congr_deriv rfl |>.congr_of_eventuallyEq ?_
    exact Filter.Eventually.of_forall fun s => by simp [orbitEnergy, div_eq_mul_inv]
  have h5 := h4.unique hloss
  unfold quadrupolePower at h5
  have hG' : G ≠ 0 := hG.ne'
  have hc' : c ≠ 0 := hc.ne'
  have hm₁' : m₁ ≠ 0 := hm₁.ne'
  have hm₂' : m₂ ≠ 0 := hm₂.ne'
  field_simp at h5 ⊢
  nlinarith [h5]
-- ANCHOR_END: shrink_rate_of_energy_loss

-- ANCHOR: chirp_rate_cubed
/-- **The rate of the frequency, with the chirp mass.** On a circular orbit,
Kepler's third law `ω² a³ = G (m₁ + m₂)` holds at every instant (`hK`), and the
separation shrinks as above (`hshrink`). Then the rate of change `ω'` of the
angular frequency satisfies `(ω')³ = (96/5)³ (G 𝓜 / c³)⁵ ω¹¹`, where `𝓜` is
defined by `𝓜⁵ = (m₁ m₂)³ / (m₁ + m₂)`. The cube is the exact form of the power
`ω^(11/3)` of the lesson. -/
theorem chirp_rate_cubed
    (G c m₁ m₂ Mc : ℝ) (ω a : ℝ → ℝ) (ω' a' t : ℝ)
    (hG : 0 < G) (hc : 0 < c) (hm₁ : 0 < m₁) (hm₂ : 0 < m₂)
    (hMc5 : Mc ^ 5 = (m₁ * m₂) ^ 3 / (m₁ + m₂))
    (ha0 : 0 < a t)
    (hω : HasDerivAt ω ω' t) (ha : HasDerivAt a a' t)
    (hK : ∀ s, ω s ^ 2 * a s ^ 3 = G * (m₁ + m₂))
    (hshrink : a' = -(64 / 5) * G ^ 3 * m₁ * m₂ * (m₁ + m₂) / (c ^ 5 * a t ^ 3)) :
    ω' ^ 3 = (96 / 5) ^ 3 * (G * Mc / c ^ 3) ^ 5 * ω t ^ 11 := by
  have hne : a t ≠ 0 := ha0.ne'
  -- Differentiating Kepler's law along the orbit: `2 ω ω' a³ + 3 ω² a² a' = 0`.
  have hprod := (hω.pow 2).mul (ha.pow 3)
  have hconst : HasDerivAt (fun s => ω s ^ 2 * a s ^ 3) 0 t := by
    have : (fun s => ω s ^ 2 * a s ^ 3) = fun _ => G * (m₁ + m₂) := funext hK
    rw [this]; exact hasDerivAt_const t _
  have hd := hprod.unique hconst
  simp at hd
  have hsum : 2 * ω t * ω' * a t ^ 3 + 3 * ω t ^ 2 * a t ^ 2 * a' = 0 := by
    nlinarith [hd]
  have hK0 := hK t
  have hM : 0 < m₁ + m₂ := by positivity
  have hM' : m₁ + m₂ ≠ 0 := hM.ne'
  have hG' : G ≠ 0 := hG.ne'
  have hc' : c ≠ 0 := hc.ne'
  have hω0 : ω t ≠ 0 := by
    intro h
    rw [h] at hK0
    have : 0 < G * (m₁ + m₂) := by positivity
    nlinarith [hK0]
  -- `ω' = (96/5) ω G³ m₁ m₂ M / (c⁵ a⁴)`.
  have hrate : ω' = 96 / 5 * ω t * G ^ 3 * m₁ * m₂ * (m₁ + m₂) / (c ^ 5 * a t ^ 4) := by
    rw [hshrink] at hsum
    field_simp at hsum ⊢
    have h2 : ω t * (2 * ω' * a t ^ 4 * 5 * c ^ 5 - ω t * 3 * 64 * G ^ 3 * m₁ * m₂ * (m₁ + m₂)) = 0 := by
      linarith [hsum]
    have h3 := (mul_eq_zero.mp h2).resolve_left hω0
    have h4 : (a t ^ 4 * c ^ 5) * ω' * 10 = ω t * 192 * G ^ 3 * m₁ * m₂ * (m₁ + m₂) := by
      linarith [h3]
    linarith [h4]
  -- Kepler's law gives `a³`, and the cube of `a⁴` is `(a³)⁴`.
  have ha3 : a t ^ 3 = G * (m₁ + m₂) / ω t ^ 2 := by
    field_simp; linarith [hK0]
  have h12 : (a t ^ 4) ^ 3 = (G * (m₁ + m₂) / ω t ^ 2) ^ 4 := by
    rw [← ha3]; ring
  have hMc' : (G * Mc / c ^ 3) ^ 5 = G ^ 5 * ((m₁ * m₂) ^ 3 / (m₁ + m₂)) / c ^ 15 := by
    rw [div_pow, mul_pow, hMc5]; ring
  have hden : (c ^ 5 * a t ^ 4) ^ 3 = c ^ 15 * (G * (m₁ + m₂) / ω t ^ 2) ^ 4 := by
    rw [mul_pow, h12]; ring
  rw [hrate, hMc', div_pow, hden]
  field_simp
-- ANCHOR_END: chirp_rate_cubed

-- ANCHOR: chirp_mass_from_rate
/-- **The chirp mass follows from a frequency and its rate.** If a frequency
`ω ≠ 0` changes at the rate `ω'` as the chirp law says, then
`(G 𝓜 / c³)⁵ = (5/96)³ (ω')³ / ω¹¹`: the relation can be solved for the chirp
mass. -/
theorem chirp_mass_from_rate
    (G c Mc ω ω' : ℝ) (hω : ω ≠ 0)
    (h : ω' ^ 3 = (96 / 5) ^ 3 * (G * Mc / c ^ 3) ^ 5 * ω ^ 11) :
    (G * Mc / c ^ 3) ^ 5 = (5 / 96) ^ 3 * ω' ^ 3 / ω ^ 11 := by
  rw [h]
  field_simp

/-- **A frequency and its rate fix one chirp mass.** Two positive chirp masses
that both satisfy the law with the same `ω` and `ω'` are equal. -/
theorem chirp_mass_unique
    (G c Mc₁ Mc₂ ω ω' : ℝ) (hG : 0 < G) (hc : 0 < c)
    (h₁ : 0 < Mc₁) (h₂ : 0 < Mc₂) (hω : ω ≠ 0)
    (e₁ : ω' ^ 3 = (96 / 5) ^ 3 * (G * Mc₁ / c ^ 3) ^ 5 * ω ^ 11)
    (e₂ : ω' ^ 3 = (96 / 5) ^ 3 * (G * Mc₂ / c ^ 3) ^ 5 * ω ^ 11) :
    Mc₁ = Mc₂ := by
  have hp : (G * Mc₁ / c ^ 3) ^ 5 = (G * Mc₂ / c ^ 3) ^ 5 := by
    rw [chirp_mass_from_rate G c Mc₁ ω ω' hω e₁,
      chirp_mass_from_rate G c Mc₂ ω ω' hω e₂]
  have hq : G * Mc₁ / c ^ 3 = G * Mc₂ / c ^ 3 :=
    (pow_left_inj₀ (by positivity) (by positivity) (by norm_num)).mp hp
  have hc3 : c ^ 3 ≠ 0 := by positivity
  rw [div_left_inj' hc3] at hq
  exact mul_left_cancel₀ hG.ne' hq
-- ANCHOR_END: chirp_mass_from_rate

-- ANCHOR: coalescence_countdown
/-- **The time to coalescence counts down at the rate one, locally.** The
angular frequency `w` has the rate `w1 t` at the instant `t`, the rate `w1` is
itself differentiable there, the law `w1³ = K w¹¹` holds on a neighbourhood of
`t` (`hlaw`), and the frequency is rising (`hrise`). Then `τ = 3 w / (8 w1)`
has the derivative `-1` at `t`. This is a local identity: it says `τ` is the
time left until the frequency diverges, `(5/256)(π f)^(-8/3)(G𝓜/c³)^(-5/3)` of
the lesson, only once the inspiral is known to reach the divergence. -/
theorem coalescence_countdown
    (K t w2 : ℝ) (w w1 : ℝ → ℝ)
    (hw : HasDerivAt w (w1 t) t) (hw1 : HasDerivAt w1 w2 t)
    (hlaw : ∀ᶠ s in nhds t, w1 s ^ 3 = K * w s ^ 11) (hrise : 0 < w1 t) :
    HasDerivAt (fun s => 3 * w s / (8 * w1 s)) (-1) t := by
  -- Differentiating the law along the inspiral: `3 w1² w2 = 11 K w¹⁰ w1`.
  have hlhs := (hw1.pow 3)
  have hrhs := (hw.pow 11).const_mul K
  have hev : (fun y => K * (w ^ 11) y) =ᶠ[nhds t] w1 ^ 3 :=
    hlaw.mono fun s hs => hs.symm
  have hd := (hlhs.congr_of_eventuallyEq hev).unique hrhs
  simp at hd
  have hw2 : 3 * w1 t * w2 = 11 * K * w t ^ 10 := by
    have hpos : w1 t ≠ 0 := hrise.ne'
    have : w1 t * (3 * w1 t * w2 - 11 * K * w t ^ 10) = 0 := by
      nlinarith [hd]
    have := (mul_eq_zero.mp this).resolve_left hpos
    linarith
  have hq := ((hw.const_mul 3).div (hw1.const_mul 8) (by positivity))
  refine hq.congr_deriv ?_
  have h8 : w1 t ≠ 0 := hrise.ne'
  have hlt := hlaw.self_of_nhds
  have key : w1 t * (3 * w t * w2 - 11 * w1 t ^ 2) = 0 := by
    have e : 3 * w1 t * w2 * w t = 11 * K * w t ^ 10 * w t := by rw [hw2]
    nlinarith [e, hlt]
  have key' := (mul_eq_zero.mp key).resolve_left h8
  field_simp
  linarith [key']
-- ANCHOR_END: coalescence_countdown

end PhysicsByConstruction.Mechanics
