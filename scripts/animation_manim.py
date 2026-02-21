"""
Metazooa – Manim Animations (minimal text edition)
====================================================
Run a single scene:
    manim -pql main.py Chapter1_01_HookQuestion
    manim -pqh main.py Chapter2_03_LCAMeet      # high quality

All scenes:
    Chapter1_01_HookQuestion
    Chapter1_02_BestFirstGuess
    Chapter1_03_EntropyEquation

    Chapter2_01_ToyTreeBuild
    Chapter2_02_GuessAndPath
    Chapter2_03_LCAMeet
    Chapter2_04_EliminateOutside
    Chapter2_05_BalancedVsUnbalanced
    Chapter2_06_MultiGuessCollapse

    Chapter3_01_EqualProbabilities
    Chapter3_02_SplitAndBars
    Chapter3_03_SurpriseGraph
    Chapter3_04_EntropyExpectedValue
    Chapter3_05_EntropyComparison

    Chapter4_01_ScaleReveal
    Chapter4_02_BucketFormation
    Chapter4_03_EntropyScan
    Chapter4_04_LeaderboardReveal

    Chapter5_01_WorstCase
    Chapter5_02_EntropyVsMinmax
    Chapter5_03_Convergence
    Chapter5_04_MinmaxLeaderboard

    Chapter7_01_MinkAnswer
    Chapter7_02_BiggerIdea
"""

import math
from manim import *

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#0F1117"
TEXT_COL  = "#F0F0F0"
ACCENT    = "#3B82F6"   # blue  – guess node
GREEN_COL = "#10B981"   # green – answer / survivors
AMBER_COL = "#F59E0B"   # amber – LCA
MUTED     = "#374151"   # gray  – eliminated
NODE_FILL = "#1E293B"
EDGE_COL  = "#334155"
RED_COL   = "#EF4444"

config.background_color = BG


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def node(pos, radius=0.27, fill=NODE_FILL, stroke=EDGE_COL):
    c = Circle(radius=radius, fill_color=fill, fill_opacity=1,
               stroke_color=stroke, stroke_width=2)
    c.move_to(pos)
    return c


def leaf_node(pos, label, font_size=16):
    c = node(pos)
    t = Text(label, font_size=font_size, color=TEXT_COL)
    t.next_to(c, DOWN, buff=0.12)
    return VGroup(c, t)


def internal_node(pos, radius=0.22):
    c = node(pos, radius=radius, fill="#1E3A5F", stroke="#4B6FA8")
    return VGroup(c)


def make_edge(a_group, b_group):
    return Line(
        a_group[0].get_center(),
        b_group[0].get_center(),
        color=EDGE_COL, stroke_width=2,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Tree definition
# ─────────────────────────────────────────────────────────────────────────────

_YL = -2.6   # leaves
_Y2 = -0.9   # Mammalia / Arthropoda
_Y1 =  0.6   # Vertebrata
_Y0 =  2.0   # root

POS = {
    "Wolf":       np.array([-5.0, _YL, 0]),
    "Cat":        np.array([-3.6, _YL, 0]),
    "Rabbit":     np.array([-2.2, _YL, 0]),
    "Eagle":      np.array([-0.7, _YL, 0]),
    "Lizard":     np.array([ 0.6, _YL, 0]),
    "Bee":        np.array([ 2.1, _YL, 0]),
    "Crab":       np.array([ 3.5, _YL, 0]),
    "Mammalia":   np.array([-3.6, _Y2,  0]),
    "Vertebrata": np.array([-1.0, _Y1,  0]),
    "Arthropoda": np.array([ 2.8, _Y2,  0]),
    "Root":       np.array([ 0.9, _Y0,  0]),
}

LEAVES   = ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard", "Bee", "Crab"]
INTERNAL = ["Mammalia", "Vertebrata", "Arthropoda", "Root"]

EDGES = [
    ("Root",       "Vertebrata"),
    ("Root",       "Arthropoda"),
    ("Vertebrata", "Mammalia"),
    ("Vertebrata", "Eagle"),
    ("Vertebrata", "Lizard"),
    ("Arthropoda", "Bee"),
    ("Arthropoda", "Crab"),
    ("Mammalia",   "Wolf"),
    ("Mammalia",   "Cat"),
    ("Mammalia",   "Rabbit"),
]


def build_tree():
    N = {}
    for name in LEAVES:
        N[name] = leaf_node(POS[name], name)
    for name in INTERNAL:
        N[name] = internal_node(POS[name])
    E = {(p, c): make_edge(N[p], N[c]) for p, c in EDGES}
    return N, E


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 1
# ─────────────────────────────────────────────────────────────────────────────

class Chapter1_01_HookQuestion(Scene):
    def construct(self):
        phrases = [
            "Guess an animal.",
            "Any animal.",
            "I give you one hint.",
            "The clade you share\nwith your guess.",
            "That's it.",
            "How would you even start?",
        ]

        prev = None
        for i, phrase in enumerate(phrases):
            size = 36 if "\n" in phrase else 48
            t = Text(phrase, font_size=size, color=TEXT_COL, line_spacing=1.5)
            t.move_to(ORIGIN)

            if prev is None:
                self.play(FadeIn(t, shift=UP * 0.15), run_time=0.6)
            else:
                self.play(FadeOut(prev, shift=UP * 0.12), run_time=0.35)
                self.play(FadeIn(t,    shift=UP * 0.15), run_time=0.55)

            hold = 2.8 if i == len(phrases) - 1 else 1.8
            self.wait(hold)
            prev = t

        self.play(FadeOut(prev))


class Chapter1_02_BestFirstGuess(Scene):
    def construct(self):
        q = Text("Best first guess?", font_size=72, color=TEXT_COL, weight=BOLD)
        underline = Line(
            q.get_left(), q.get_right(),
            color=ACCENT, stroke_width=3,
        ).next_to(q, DOWN, buff=0.18)

        self.play(Write(q), run_time=0.9)
        self.play(Create(underline), run_time=0.5)
        self.wait(3)
        self.play(FadeOut(VGroup(q, underline)))


class Chapter1_03_EntropyEquation(Scene):
    def construct(self):
        formula = MathTex(
            r"H = -\sum_i p_i \log_2 p_i",
            font_size=62, color=TEXT_COL,
        )
        bg = SurroundingRectangle(
            formula, color=NODE_FILL, fill_color=NODE_FILL,
            fill_opacity=0.82, buff=0.5, corner_radius=0.18, stroke_width=0,
        )
        self.play(FadeIn(bg))
        self.play(Write(formula), run_time=1.8)
        self.wait(3)
        self.play(FadeOut(VGroup(bg, formula)))


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 2
# ─────────────────────────────────────────────────────────────────────────────

class Chapter2_01_ToyTreeBuild(Scene):
    def construct(self):
        N, E = build_tree()

        levels = [
            ([], ["Root"]),
            ([("Root","Vertebrata"), ("Root","Arthropoda")],
             ["Vertebrata", "Arthropoda"]),
            ([("Vertebrata","Mammalia"), ("Vertebrata","Eagle"),
              ("Vertebrata","Lizard"),  ("Arthropoda","Bee"),
              ("Arthropoda","Crab")],
             ["Mammalia", "Eagle", "Lizard", "Bee", "Crab"]),
            ([("Mammalia","Wolf"), ("Mammalia","Cat"), ("Mammalia","Rabbit")],
             ["Wolf", "Cat", "Rabbit"]),
        ]

        for edge_keys, node_names in levels:
            anims = (
                [Create(E[k]) for k in edge_keys] +
                [FadeIn(N[n], scale=0.7) for n in node_names]
            )
            self.play(*anims, run_time=0.7, lag_ratio=0.1)
            self.wait(0.3)

        self.wait(2)


class Chapter2_02_GuessAndPath(Scene):
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        self.play(
            N["Wolf"][0].animate.set_fill(ACCENT).set_stroke(ACCENT, width=3),
            run_time=0.6,
        )
        self.wait(0.6)
        self.play(
            N["Cat"][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3),
            run_time=0.6,
        )
        self.wait(2)


class Chapter2_03_LCAMeet(Scene):
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        N["Wolf"][0].set_fill(ACCENT).set_stroke(ACCENT, width=3)
        N["Cat"][0].set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3)

        def hi_edge(key, color):
            return E[key].copy().set_color(color).set_stroke_width(4)

        self.play(Create(hi_edge(("Mammalia","Wolf"), ACCENT)),     run_time=0.5)
        self.play(Create(hi_edge(("Mammalia","Cat"),  GREEN_COL)),  run_time=0.5)
        self.wait(0.3)

        self.play(
            N["Mammalia"][0].animate
                .set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3).scale(1.25),
            run_time=0.5,
        )
        self.play(N["Mammalia"][0].animate.scale(1 / 1.25), run_time=0.3)

        tag = Text("LCA", font_size=20, color=AMBER_COL, weight=BOLD)
        tag.next_to(N["Mammalia"][0], RIGHT, buff=0.22)
        self.play(FadeIn(tag, scale=0.8), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(tag))


class Chapter2_04_EliminateOutside(Scene):
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        N["Wolf"][0].set_fill(ACCENT).set_stroke(ACCENT, width=3)
        N["Cat"][0].set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3)
        N["Mammalia"][0].set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3)

        inside_nodes = {"Mammalia", "Wolf", "Cat", "Rabbit"}
        inside_edges = {("Mammalia","Wolf"), ("Mammalia","Cat"), ("Mammalia","Rabbit")}
        outside_nodes = [n for n in LEAVES + INTERNAL if n not in inside_nodes]
        outside_edges = [k for k in EDGES if k not in inside_edges]

        dim = []
        for name in outside_nodes:
            dim.append(N[name][0].animate.set_fill(MUTED, opacity=0.12)
                                          .set_stroke(MUTED, opacity=0.12))
            if len(N[name]) > 1:
                dim.append(N[name][1].animate.set_opacity(0.12))
        for k in outside_edges:
            dim.append(E[k].animate.set_stroke(MUTED, opacity=0.10))

        self.play(*dim, run_time=1.1, lag_ratio=0.04)
        self.wait(0.6)

        survivors = ["Wolf", "Cat", "Rabbit"]
        self.play(
            *[N[n][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=2)
              for n in survivors],
            run_time=0.5,
        )
        self.play(*[N[n][0].animate.scale(1.15) for n in survivors], run_time=0.3)
        self.play(*[N[n][0].animate.scale(1/1.15) for n in survivors], run_time=0.3)
        self.wait(2.5)


class Chapter2_05_BalancedVsUnbalanced(Scene):
    def construct(self):
        def dot_row(n, color, x_start, y, spacing=0.62):
            return VGroup(*[
                Circle(radius=0.21, fill_color=color, fill_opacity=1, stroke_width=0)
                .move_to(np.array([x_start + i * spacing, y, 0]))
                for i in range(n)
            ])

        big    = dot_row(5, ACCENT,     -4.6,  0.4)
        small  = dot_row(2, GREEN_COL,  -4.6, -0.5)
        label_l = Text("5 : 2", font_size=26, color=MUTED).move_to([-3.3, 1.6, 0])

        div = DashedLine([-1.2, 2.0, 0], [-1.2, -1.5, 0],
                         color=EDGE_COL, stroke_width=1.5)

        half_a  = dot_row(3, ACCENT,     0.2,  0.4)
        half_b  = dot_row(4, GREEN_COL,  0.2, -0.5)
        label_r = Text("3 : 4", font_size=26, color=MUTED).move_to([ 1.5, 1.6, 0])

        self.play(FadeIn(label_l), run_time=0.3)
        self.play(FadeIn(big, shift=UP * 0.1), run_time=0.5, lag_ratio=0.1)
        self.play(FadeIn(small), run_time=0.4)
        self.wait(0.5)

        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(label_r), run_time=0.3)
        self.play(
            FadeIn(half_a, shift=UP * 0.1),
            FadeIn(half_b, shift=DOWN * 0.1),
            run_time=0.5, lag_ratio=0.1,
        )
        self.wait(0.8)

        bad_brace = Brace(big, direction=UP, color=RED_COL)
        self.play(GrowFromCenter(bad_brace), run_time=0.5)
        self.wait(1.2)

        good_box = SurroundingRectangle(
            VGroup(half_a, half_b),
            color=GREEN_COL, corner_radius=0.12,
            stroke_width=2, buff=0.2,
        )
        self.play(Create(good_box), run_time=0.5)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            label_l, label_r, big, small, half_a, half_b,
            div, bad_brace, good_box,
        )))


class Chapter2_06_MultiGuessCollapse(Scene):
    """
    Three sequential guesses narrow the tree to a single animal.
    Guess 1: Wolf  → LCA = Mammalia → eliminates Eagle, Lizard, Bee, Crab
    Guess 2: Rabbit → wrong, dims itself
    Guess 3: Cat   → correct, win flash
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        counter_bg = RoundedRectangle(
            width=2.2, height=0.55, corner_radius=0.12,
            fill_color=NODE_FILL, fill_opacity=0.9, stroke_width=0,
        ).to_corner(UR, buff=0.45)
        counter_lbl = Text("Guess 1", font_size=22, color=MUTED)
        counter_lbl.move_to(counter_bg.get_center())
        self.add(counter_bg, counter_lbl)

        # ── Guess 1: Wolf ──────────────────────────────────────────────────
        self.play(
            N["Wolf"][0].animate.set_fill(ACCENT).set_stroke(ACCENT, width=3),
            run_time=0.5,
        )
        self.wait(0.4)

        self.play(
            N["Mammalia"][0].animate
                .set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3).scale(1.25),
            run_time=0.5,
        )
        self.play(N["Mammalia"][0].animate.scale(1 / 1.25), run_time=0.3)

        outside_nodes = ["Eagle", "Lizard", "Bee", "Crab", "Arthropoda", "Vertebrata", "Root"]
        outside_edges = [("Vertebrata","Eagle"), ("Vertebrata","Lizard"),
                         ("Arthropoda","Bee"),   ("Arthropoda","Crab"),
                         ("Root","Vertebrata"),  ("Root","Arthropoda")]

        dim_anims = []
        for name in outside_nodes:
            dim_anims.append(N[name][0].animate.set_fill(MUTED, opacity=0.12)
                                                .set_stroke(MUTED, opacity=0.12))
            if len(N[name]) > 1:
                dim_anims.append(N[name][1].animate.set_opacity(0.12))
        for k in outside_edges:
            dim_anims.append(E[k].animate.set_stroke(MUTED, opacity=0.10))

        self.play(*dim_anims, run_time=1.0, lag_ratio=0.05)
        self.play(
            *[N[n][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=2)
              for n in ["Cat", "Rabbit"]],
            run_time=0.5,
        )
        self.wait(0.9)

        # ── Guess 2: Rabbit ────────────────────────────────────────────────
        new_counter = Text("Guess 2", font_size=22, color=MUTED)
        new_counter.move_to(counter_bg.get_center())
        self.play(Transform(counter_lbl, new_counter), run_time=0.3)

        self.play(
            N["Rabbit"][0].animate.set_fill(ACCENT).set_stroke(ACCENT, width=3),
            run_time=0.5,
        )
        self.wait(0.5)
        self.play(
            N["Rabbit"][0].animate.set_fill(MUTED, opacity=0.12)
                                   .set_stroke(MUTED, opacity=0.12),
            N["Rabbit"][1].animate.set_opacity(0.12),
            E[("Mammalia","Rabbit")].animate.set_stroke(MUTED, opacity=0.10),
            run_time=0.8,
        )
        self.play(
            N["Cat"][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=2),
            run_time=0.4,
        )
        self.wait(0.9)

        # ── Guess 3: Cat ───────────────────────────────────────────────────
        new_counter2 = Text("Guess 3", font_size=22, color=AMBER_COL, weight=BOLD)
        new_counter2.move_to(counter_bg.get_center())
        self.play(Transform(counter_lbl, new_counter2), run_time=0.3)

        self.play(
            N["Cat"][0].animate.set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3)
                        .scale(1.35),
            run_time=0.6,
        )
        self.play(N["Cat"][0].animate.scale(1 / 1.35), run_time=0.3)
        self.play(
            N["Cat"][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3),
            N["Mammalia"][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=2),
            run_time=0.5,
        )

        tick = Text("✓", font_size=64, color=GREEN_COL)
        tick.next_to(N["Cat"][0], UP, buff=0.22)
        self.play(FadeIn(tick, scale=0.4), run_time=0.4)
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 3
# ─────────────────────────────────────────────────────────────────────────────

class Chapter3_01_EqualProbabilities(Scene):
    def construct(self):
        N, E = build_tree()

        levels = [
            ([], ["Root"]),
            ([("Root","Vertebrata"), ("Root","Arthropoda")],
             ["Vertebrata", "Arthropoda"]),
            ([("Vertebrata","Mammalia"), ("Vertebrata","Eagle"),
              ("Vertebrata","Lizard"),  ("Arthropoda","Bee"),
              ("Arthropoda","Crab")],
             ["Mammalia", "Eagle", "Lizard", "Bee", "Crab"]),
            ([("Mammalia","Wolf"), ("Mammalia","Cat"), ("Mammalia","Rabbit")],
             ["Wolf", "Cat", "Rabbit"]),
        ]
        for edge_keys, node_names in levels:
            anims = (
                [Create(E[k]) for k in edge_keys] +
                [FadeIn(N[n], scale=0.7) for n in node_names]
            )
            self.play(*anims, run_time=0.55, lag_ratio=0.1)

        self.wait(0.5)

        fracs = VGroup(*[
            MathTex(r"\tfrac{1}{7}", font_size=19, color=MUTED)
            .next_to(N[name][0], UP, buff=0.12)
            for name in LEAVES
        ])
        self.play(FadeIn(fracs, lag_ratio=0.12), run_time=1.0)
        self.wait(0.4)

        self.play(
            *[N[name][0].animate.set_fill(ACCENT, opacity=0.6)
                                  .set_stroke(ACCENT, width=2)
              for name in LEAVES],
            run_time=0.7,
        )
        self.wait(2.5)


class Chapter3_02_SplitAndBars(Scene):
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        big_leaves   = ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard"]
        small_leaves = ["Bee", "Crab"]

        self.play(
            *[N[n][0].animate.set_fill(ACCENT,    opacity=0.85)
                               .set_stroke(ACCENT,    width=2) for n in big_leaves],
            *[N[n][0].animate.set_fill(GREEN_COL, opacity=0.85)
                               .set_stroke(GREEN_COL, width=2) for n in small_leaves],
            run_time=0.8,
        )
        self.wait(0.5)

        ell_big = SurroundingRectangle(
            VGroup(*[N[n][0] for n in big_leaves]),
            color=ACCENT, corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )
        ell_small = SurroundingRectangle(
            VGroup(*[N[n][0] for n in small_leaves]),
            color=GREEN_COL, corner_radius=0.35, stroke_width=2.5, buff=0.32,
        )
        self.play(Create(ell_big), Create(ell_small), run_time=0.7)
        self.wait(1.8)

        balanced_blue  = ["Wolf", "Cat", "Rabbit"]
        balanced_green = ["Eagle", "Lizard", "Bee", "Crab"]

        new_ell_blue = SurroundingRectangle(
            VGroup(*[N[n][0] for n in balanced_blue]),
            color=ACCENT, corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )
        new_ell_green = SurroundingRectangle(
            VGroup(*[N[n][0] for n in balanced_green]),
            color=GREEN_COL, corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )

        self.play(
            *[N[n][0].animate.set_fill(ACCENT,    opacity=0.85)
                               .set_stroke(ACCENT,    width=2) for n in balanced_blue],
            *[N[n][0].animate.set_fill(GREEN_COL, opacity=0.85)
                               .set_stroke(GREEN_COL, width=2) for n in balanced_green],
            Transform(ell_big,   new_ell_blue),
            Transform(ell_small, new_ell_green),
            run_time=1.0,
        )
        self.wait(2.5)


class Chapter3_03_SurpriseGraph(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 1.05, 0.25],
            y_range=[0, 4.2,  1],
            x_length=6.5,
            y_length=4.5,
            axis_config={
                "color": EDGE_COL, "stroke_width": 2,
                "include_tip": True, "tip_width": 0.18, "tip_height": 0.18,
            },
            x_axis_config={"numbers_to_include": [0.25, 0.5, 0.75, 1.0],
                           "font_size": 20, "color": MUTED},
            y_axis_config={"numbers_to_include": [1, 2, 3, 4],
                           "font_size": 20, "color": MUTED},
        ).move_to(ORIGIN + LEFT * 0.5)

        x_label = MathTex("p",    font_size=28, color=MUTED) \
            .next_to(ax.x_axis.get_right(), RIGHT, buff=0.15)
        y_label = MathTex("I(p)", font_size=28, color=MUTED) \
            .next_to(ax.y_axis.get_top(),   UP,    buff=0.12)
        formula = MathTex(r"I(p) = -\log_2 p", font_size=28, color=ACCENT) \
            .to_corner(UR, buff=0.5)

        curve = ax.plot(lambda p: -np.log2(p), x_range=[0.06, 1.0],
                        color=ACCENT, stroke_width=3)

        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label), run_time=1.0)
        self.play(Create(curve), run_time=1.2)
        self.play(Write(formula), run_time=0.8)
        self.wait(0.5)

        highlights = [
            (0.5,   1, "1 \\ \\text{bit}"),
            (0.25,  2, "2 \\ \\text{bits}"),
            (0.125, 3, "3 \\ \\text{bits}"),
        ]

        for p_val, bits, label_str in highlights:
            pt = ax.coords_to_point(p_val, bits)
            dot = Dot(pt, color=AMBER_COL, radius=0.09)
            v_line = DashedLine(ax.coords_to_point(p_val, 0), pt,
                                color=MUTED, stroke_width=1.5, dash_length=0.1)
            h_line = DashedLine(ax.coords_to_point(0, bits), pt,
                                color=MUTED, stroke_width=1.5, dash_length=0.1)
            bit_label = MathTex(label_str, font_size=22, color=AMBER_COL) \
                .next_to(dot, RIGHT, buff=0.18)

            self.play(Create(v_line), Create(h_line), run_time=0.4)
            self.play(FadeIn(dot, scale=0.5), FadeIn(bit_label), run_time=0.4)
            self.wait(0.9)

        self.wait(2)


class Chapter3_04_EntropyExpectedValue(Scene):
    """
    Two panels, left = 5:2 split, right = 3:4 split.
    Panels reveal one at a time. After both, dim left and pulse right H value.
    """

    def _make_panel(self, x_center, p_left, p_right,
                    col_left, col_right, n_left, n_right, denom=7):
        top   = np.array([x_center,  2.2, 0])
        bot_l = np.array([x_center - 1.55, -0.1, 0])
        bot_r = np.array([x_center + 1.55, -0.1, 0])

        root   = Dot(top, color=MUTED, radius=0.10)
        line_l = Line(top, bot_l, color=EDGE_COL, stroke_width=1.8)
        line_r = Line(top, bot_r, color=EDGE_COL, stroke_width=1.8)

        def dot_cluster(n, color, center):
            spacing = 0.28
            total_w = (n - 1) * spacing
            return VGroup(*[
                Circle(radius=0.10, fill_color=color, fill_opacity=1, stroke_width=0)
                .move_to(center + LEFT * total_w / 2 + RIGHT * spacing * i)
                for i in range(n)
            ])

        cluster_l = dot_cluster(n_left,  col_left,  bot_l)
        cluster_r = dot_cluster(n_right, col_right, bot_r)

        p_lbl_l = MathTex(
            rf"p = \tfrac{{{int(round(p_left  * denom))}}}{{{denom}}}",
            font_size=20, color=col_left,
        ).next_to(line_l.get_center(), LEFT, buff=0.08)
        p_lbl_r = MathTex(
            rf"p = \tfrac{{{int(round(p_right * denom))}}}{{{denom}}}",
            font_size=20, color=col_right,
        ).next_to(line_r.get_center(), RIGHT, buff=0.08)

        I_left  = -math.log2(p_left)
        I_right = -math.log2(p_right)

        I_formula_l = MathTex(
            rf"I = -\log_2\!\bigl(\tfrac{{{int(round(p_left  * denom))}}}{{{denom}}}\bigr)",
            font_size=18, color=MUTED,
        ).next_to(cluster_l, DOWN, buff=0.18)
        I_formula_r = MathTex(
            rf"I = -\log_2\!\bigl(\tfrac{{{int(round(p_right * denom))}}}{{{denom}}}\bigr)",
            font_size=18, color=MUTED,
        ).next_to(cluster_r, DOWN, buff=0.18)

        I_dec_l = MathTex(rf"\approx {I_left:.2f}",  font_size=18, color=MUTED)\
            .next_to(I_formula_l, RIGHT, buff=0.08)
        I_dec_r = MathTex(rf"\approx {I_right:.2f}", font_size=18, color=MUTED)\
            .next_to(I_formula_r, RIGHT, buff=0.08)

        w_left  = p_left  * I_left
        w_right = p_right * I_right

        w_lbl_l = MathTex(rf"p \cdot I \approx {w_left:.2f}",
                           font_size=18, color=col_left)\
            .next_to(I_dec_l, DOWN, buff=0.15)
        w_lbl_r = MathTex(rf"p \cdot I \approx {w_right:.2f}",
                           font_size=18, color=col_right)\
            .next_to(I_dec_r, DOWN, buff=0.15)

        H_val = w_left + w_right
        H_lbl = MathTex(
            rf"H = {w_left:.2f} + {w_right:.2f} = {H_val:.2f}\ \text{{bits}}",
            font_size=20, color=TEXT_COL,
        ).next_to(VGroup(w_lbl_l, w_lbl_r), DOWN, buff=0.28)

        structure = VGroup(root, line_l, line_r, cluster_l, cluster_r)
        steps = [
            VGroup(p_lbl_l, p_lbl_r),
            VGroup(I_formula_l, I_formula_r),
            VGroup(I_dec_l,     I_dec_r),
            VGroup(w_lbl_l,     w_lbl_r),
            H_lbl,
        ]
        return structure, steps, H_val

    def construct(self):
        lbl_A = Text("5 : 2", font_size=22, color=MUTED).move_to([-3.0, 3.2, 0])
        lbl_B = Text("3 : 4", font_size=22, color=MUTED).move_to([ 3.0, 3.2, 0])
        divider = DashedLine(UP * 3.0, DOWN * 3.0, color=EDGE_COL, stroke_width=1.2)

        self.play(FadeIn(lbl_A), Create(divider), run_time=0.5)

        struct_A, steps_A, _ = self._make_panel(
            x_center=-3.0, p_left=5/7, p_right=2/7,
            col_left=ACCENT, col_right=GREEN_COL, n_left=5, n_right=2,
        )
        self.play(FadeIn(struct_A), run_time=0.6)
        self.wait(0.3)
        for step in steps_A:
            self.play(FadeIn(step), run_time=0.6)
            self.wait(0.8)

        self.wait(0.5)
        self.play(FadeIn(lbl_B), run_time=0.4)

        struct_B, steps_B, _ = self._make_panel(
            x_center=3.0, p_left=3/7, p_right=4/7,
            col_left=ACCENT, col_right=GREEN_COL, n_left=3, n_right=4,
        )
        self.play(FadeIn(struct_B), run_time=0.6)
        self.wait(0.3)
        for step in steps_B:
            self.play(FadeIn(step), run_time=0.6)
            self.wait(0.8)

        self.wait(0.4)
        self.play(
            struct_A.animate.set_opacity(0.3),
            *[s.animate.set_opacity(0.3) for s in steps_A],
            run_time=0.7,
        )
        self.play(steps_B[-1].animate.scale(1.12), run_time=0.3)
        self.play(steps_B[-1].animate.scale(1/1.12), run_time=0.25)
        self.wait(2.0)


class Chapter3_05_EntropyComparison(Scene):
    def construct(self):
        H_unbal = -(5/7)*math.log2(5/7) - (2/7)*math.log2(2/7)
        H_bal   = -(3/7)*math.log2(3/7) - (4/7)*math.log2(4/7)

        dots_left = VGroup(
            *[Circle(radius=0.18, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
              .move_to(LEFT * 4.0 + RIGHT * 0.45 * i + UP * 1.5) for i in range(5)],
            *[Circle(radius=0.18, fill_color=GREEN_COL, fill_opacity=1, stroke_width=0)
              .move_to(LEFT * 4.0 + RIGHT * 0.45 * i + UP * 0.8) for i in range(2)],
        )
        H_left_lbl = MathTex(
            rf"H = {H_unbal:.2f}\ \text{{bits}}", font_size=36, color=MUTED,
        ).move_to(LEFT * 2.8 + DOWN * 0.2)

        div = DashedLine(UP * 2.2, DOWN * 2.2, color=EDGE_COL, stroke_width=1.5)

        dots_right = VGroup(
            *[Circle(radius=0.18, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
              .move_to(RIGHT * 1.0 + RIGHT * 0.45 * i + UP * 1.5) for i in range(3)],
            *[Circle(radius=0.18, fill_color=GREEN_COL, fill_opacity=1, stroke_width=0)
              .move_to(RIGHT * 1.0 + RIGHT * 0.45 * i + UP * 0.8) for i in range(4)],
        )
        H_right_lbl = MathTex(
            rf"H = {H_bal:.2f}\ \text{{bits}}", font_size=36, color=GREEN_COL,
        ).move_to(RIGHT * 2.8 + DOWN * 0.2)

        self.play(FadeIn(dots_left), run_time=0.5)
        self.play(Write(H_left_lbl), run_time=0.8)
        self.wait(0.4)
        self.play(Create(div), run_time=0.4)
        self.play(FadeIn(dots_right), run_time=0.5)
        self.play(Write(H_right_lbl), run_time=0.8)
        self.wait(0.8)
        self.play(H_right_lbl.animate.scale(1.18), run_time=0.35)
        self.play(H_right_lbl.animate.scale(1/1.18), run_time=0.3)
        self.play(
            dots_left.animate.set_opacity(0.25),
            H_left_lbl.animate.set_opacity(0.25),
            run_time=0.7,
        )
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 4
# ─────────────────────────────────────────────────────────────────────────────

class Chapter4_01_ScaleReveal(Scene):
    """
    Toy tree fades out, replaced by a dense dot cloud.
    Counter ticks to 328 (actual Metazooa species count).
    """
    def construct(self):
        N, E = build_tree()
        tree_group = VGroup(*E.values(), *N.values())
        self.add(tree_group)
        self.wait(0.5)

        self.play(
            tree_group.animate.scale(0.18).move_to(ORIGIN).set_opacity(0.25),
            run_time=1.2,
        )
        self.wait(0.3)

        rng = np.random.default_rng(42)
        n_dots = 280
        xs = rng.uniform(-6.5, 6.5, n_dots)
        ys = rng.uniform(-3.5, 3.5, n_dots)

        cloud = VGroup(*[
            Dot(np.array([x, y, 0]), radius=0.045,
                color=EDGE_COL, fill_opacity=0.0)
            for x, y in zip(xs, ys)
        ])

        self.play(FadeOut(tree_group), FadeIn(cloud, lag_ratio=0.008), run_time=1.4)
        self.wait(0.4)
        self.play(
            cloud.animate.set_fill(color=ACCENT, opacity=0.55)
                          .set_stroke(color=ACCENT, width=0.5, opacity=0.6),
            run_time=1.0, lag_ratio=0.004,
        )

        counter_val = {"v": 0}
        counter_tex = Integer(0, font_size=52, color=TEXT_COL)
        counter_tex.to_corner(DR, buff=0.55)
        self.play(FadeIn(counter_tex), run_time=0.3)

        def update_counter(mob, dt):
            counter_val["v"] = min(counter_val["v"] + dt * 165, 328)
            mob.set_value(int(counter_val["v"]))

        counter_tex.add_updater(update_counter)
        self.wait(2.0)
        counter_tex.remove_updater(update_counter)
        counter_tex.set_value(328)
        self.wait(1.8)


class Chapter4_02_BucketFormation(Scene):
    """
    Phase 1: animals fly into buckets (LCA flash → dot arc).
    Phase 2: for each bucket, dim the tree to show the TRUE remaining
             search space. A "most specific clade" callout explains
             why Vertebrata = Eagle + Lizard only, not 5 animals.

    The key annotation for Vertebrata:
      "Mammalia would be returned instead → only Eagle & Lizard remain"
    """

    WOLF_LCAS = {
        "Wolf":   "Mammalia",
        "Cat":    "Mammalia",
        "Rabbit": "Mammalia",
        "Eagle":  "Vertebrata",
        "Lizard": "Vertebrata",
        "Bee":    "Root",
        "Crab":   "Root",
    }
    BUCKET_COLORS = {
        "Mammalia":   ACCENT,
        "Vertebrata": AMBER_COL,
        "Root":       GREEN_COL,
    }

    def construct(self):
        # ── Tree at top, scaled ────────────────────────────────────────────
        N, E = build_tree()
        tree = VGroup(*E.values(), *N.values())
        tree.scale(0.62).to_edge(UP, buff=0.3)
        self.play(FadeIn(tree, lag_ratio=0.05), run_time=1.0)

        self.play(
            N["Wolf"][0].animate.set_fill(ACCENT).set_stroke(ACCENT, width=3),
            run_time=0.5,
        )

        # Rule callout — appears once, stays for orientation
        rule_lbl = Text("game returns the most specific clade",
                        font_size=15, color=MUTED)
        rule_lbl.to_edge(DOWN, buff=0.18)
        self.play(FadeIn(rule_lbl), run_time=0.4)
        self.wait(0.3)

        # ── Three bucket boxes ─────────────────────────────────────────────
        bucket_names  = ["Mammalia", "Vertebrata", "Root"]
        bucket_x      = [-4.0, 0.0, 4.0]
        bucket_y_top  = -0.85
        bucket_height = 1.9
        bucket_width  = 3.0

        boxes    = {}
        box_lbls = {}
        for name, x in zip(bucket_names, bucket_x):
            color = self.BUCKET_COLORS[name]
            box = RoundedRectangle(
                width=bucket_width, height=bucket_height,
                corner_radius=0.18,
                fill_color=NODE_FILL, fill_opacity=0.6,
                stroke_color=color, stroke_width=2,
            ).move_to(np.array([x, bucket_y_top - bucket_height / 2, 0]))
            lbl = Text(name, font_size=18, color=color)
            lbl.next_to(box, UP, buff=0.10)
            boxes[name]    = box
            box_lbls[name] = lbl

        self.play(
            *[FadeIn(boxes[n]) for n in bucket_names],
            *[FadeIn(box_lbls[n]) for n in bucket_names],
            run_time=0.7,
        )
        self.wait(0.3)

        # ── Phase 1: animals fly into buckets ─────────────────────────────
        bucket_dot_counts = {n: 0 for n in bucket_names}
        dot_mobs = {}

        def next_dot_pos(bucket_name):
            idx = bucket_dot_counts[bucket_name]
            bx  = bucket_x[bucket_names.index(bucket_name)]
            row = idx // 3
            col = idx  % 3
            x   = bx - 0.80 + col * 0.80
            y   = bucket_y_top - 0.38 - row * 0.60
            return np.array([x, y, 0])

        for animal in ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard", "Bee", "Crab"]:
            lca      = self.WOLF_LCAS[animal]
            color    = self.BUCKET_COLORS[lca]
            lca_node = N[lca][0]

            self.play(
                lca_node.animate.set_fill(color).set_stroke(color, width=2.5),
                run_time=0.25,
            )

            leaf_center = N[animal][0].get_center()
            target_pos  = next_dot_pos(lca)
            dot     = Dot(leaf_center, radius=0.13, color=color)
            dot_lbl = Text(animal, font_size=11, color=TEXT_COL)

            self.play(FadeIn(dot, scale=0.5), run_time=0.2)
            self.play(dot.animate.move_to(target_pos),
                      run_time=0.5, rate_func=smooth)
            dot_lbl.move_to(target_pos + RIGHT * 0.30)
            self.play(FadeIn(dot_lbl), run_time=0.18)

            dot_mobs[animal] = (dot, dot_lbl)
            bucket_dot_counts[lca] += 1

            self.play(
                lca_node.animate.set_fill("#1E3A5F").set_stroke("#4B6FA8", width=2),
                run_time=0.18,
            )

        self.wait(0.8)

        # ── Phase 2: spotlight each bucket's true search space ─────────────
        #
        # The critical teaching moment is Vertebrata.  Wolf/Cat/Rabbit are
        # biologically inside Vertebrata, but the game would have returned
        # "Mammalia" for those — so a "Vertebrata" response can only mean
        # Eagle or Lizard.  We make this visible by:
        #   (a) dimming the tree to the correct survivors
        #   (b) showing a grey-out + annotation over Wolf/Cat/Rabbit for
        #       the Vertebrata bucket with the explanation.

        all_nodes     = set(LEAVES + INTERNAL)
        all_edge_keys = set(EDGES)

        # Which tree nodes to keep highlighted per bucket
        tree_highlight = {
            "Mammalia":   {"Mammalia", "Wolf", "Cat", "Rabbit"},
            "Vertebrata": {"Vertebrata", "Eagle", "Lizard"},
            "Root":       {"Arthropoda", "Bee", "Crab"},
        }
        tree_edges_keep = {
            "Mammalia":   {("Vertebrata","Mammalia"), ("Mammalia","Wolf"),
                           ("Mammalia","Cat"), ("Mammalia","Rabbit")},
            "Vertebrata": {("Root","Vertebrata"), ("Vertebrata","Eagle"),
                           ("Vertebrata","Lizard")},
            "Root":       {("Root","Arthropoda"), ("Arthropoda","Bee"),
                           ("Arthropoda","Crab")},
        }

        remaining_p = {"Mammalia": "3/7", "Vertebrata": "2/7", "Root": "2/7"}

        size_lbls = {}

        for bucket_name, bx in zip(bucket_names, bucket_x):
            color      = self.BUCKET_COLORS[bucket_name]
            keep_nodes = tree_highlight[bucket_name]
            keep_edges = tree_edges_keep[bucket_name]
            dim_nodes  = all_nodes - keep_nodes
            dim_edges  = all_edge_keys - keep_edges

            dim_anims = []
            for name in dim_nodes:
                dim_anims.append(
                    N[name][0].animate.set_fill(MUTED, opacity=0.08)
                                       .set_stroke(MUTED, opacity=0.08))
                if len(N[name]) > 1:
                    dim_anims.append(N[name][1].animate.set_opacity(0.08))
            for k in dim_edges:
                dim_anims.append(E[k].animate.set_stroke(MUTED, opacity=0.06))
            for name in keep_nodes:
                dim_anims.append(
                    N[name][0].animate.set_fill(color, opacity=0.8)
                                       .set_stroke(color, width=2.5))

            self.play(*dim_anims, run_time=0.6)

            # Size label
            s_lbl = MathTex(rf"p = {remaining_p[bucket_name]}",
                            font_size=18, color=color)
            s_lbl.next_to(boxes[bucket_name], DOWN, buff=0.10)
            self.play(FadeIn(s_lbl, shift=UP * 0.08), run_time=0.35)
            size_lbls[bucket_name] = s_lbl

            # Restore tree
            restore = []
            for name in all_nodes:
                restore.append(
                    N[name][0].animate.set_fill("#1E3A5F", opacity=1)
                                       .set_stroke("#4B6FA8", width=2))
                if len(N[name]) > 1:
                    restore.append(N[name][1].animate.set_opacity(1))
            for k in all_edge_keys:
                restore.append(E[k].animate.set_stroke(EDGE_COL, opacity=1))
            self.play(*restore, run_time=0.3)

        self.wait(2.0)


class Chapter4_03_EntropyScan(Scene):
    """
    Brute-force scan visualized as a scrolling list with growing bars.
    A cursor steps down; top 3 glow green at the end.
    """

    SCAN_DATA = [
        ("Bison",       1.165),
        ("Horse",       1.028),
        ("Mink",        1.193),
        ("Salmon",      0.692),
        ("Eagle",       1.079),
        ("Weasel",      1.191),
        ("Elephant",    0.880),
        ("Crow",        1.110),
        ("Ferret",      1.193),
        ("Koala",       0.888),
        ("Lizard",      0.973),
        ("Sea Otter",   1.189),
        ("Rabbit",      1.077),
        ("Jellyfish",   0.123),
        ("Wolf",        1.169),
    ]

    BAR_MAX_W = 3.5
    BAR_H     = 0.28

    def construct(self):
        title = Text("computing entropy for every animal…",
                     font_size=20, color=MUTED)
        title.to_edge(UP, buff=0.45)
        self.play(FadeIn(title), run_time=0.5)

        n = len(self.SCAN_DATA)
        y_positions  = [2.8 - i * 0.52 for i in range(n)]
        x_name       = -5.5
        x_bar_start  = -1.8

        name_mobs = []
        for i, (name, _) in enumerate(self.SCAN_DATA):
            t = Text(name, font_size=18, color=TEXT_COL)
            t.move_to(np.array([x_name + len(name) * 0.055, y_positions[i], 0]))
            name_mobs.append(t)

        self.play(
            LaggedStart(*[FadeIn(t, shift=RIGHT * 0.1) for t in name_mobs],
                        lag_ratio=0.06),
            run_time=1.2,
        )
        self.wait(0.3)

        cursor = Arrow(
            start=LEFT * 0.2, end=RIGHT * 0.2,
            color=AMBER_COL, buff=0, stroke_width=3,
            max_tip_length_to_length_ratio=0.5,
        )

        bars         = []
        score_labels = []

        for i, (name, score) in enumerate(self.SCAN_DATA):
            y = y_positions[i]
            cursor.move_to(np.array([-3.2, y, 0]))
            if i == 0:
                self.play(FadeIn(cursor), run_time=0.2)
            else:
                self.play(cursor.animate.move_to(np.array([-3.2, y, 0])),
                          run_time=0.18)

            bar_w = (score / 1.2) * self.BAR_MAX_W
            bar = Rectangle(
                width=bar_w, height=self.BAR_H,
                fill_color=ACCENT, fill_opacity=0.85, stroke_width=0,
            )
            bar.move_to(np.array([x_bar_start + bar_w / 2, y, 0]))
            score_lbl = Text(f"{score:.3f}", font_size=14, color=MUTED)
            score_lbl.next_to(bar, RIGHT, buff=0.10)

            self.play(GrowFromEdge(bar, edge=LEFT), run_time=0.22)
            self.play(FadeIn(score_lbl), run_time=0.12)

            bars.append(bar)
            score_labels.append(score_lbl)

        self.play(FadeOut(cursor), run_time=0.3)
        self.wait(0.5)

        sorted_indices = sorted(range(n),
                                key=lambda i: self.SCAN_DATA[i][1],
                                reverse=True)
        top3 = sorted_indices[:3]
        rest = [i for i in range(n) if i not in top3]

        self.play(
            *[bars[i].animate.set_fill(GREEN_COL) for i in top3],
            *[name_mobs[i].animate.set_color(GREEN_COL) for i in top3],
            *[score_labels[i].animate.set_color(GREEN_COL) for i in top3],
            run_time=0.7,
        )
        self.play(
            *[bars[i].animate.set_opacity(0.18)         for i in rest],
            *[name_mobs[i].animate.set_opacity(0.25)    for i in rest],
            *[score_labels[i].animate.set_opacity(0.18) for i in rest],
            run_time=0.6,
        )
        self.wait(2.5)


class Chapter4_04_LeaderboardReveal(Scene):
    """
    Real experimental numbers. Mink and Ferret tied at 1.1927.
    """
    def construct(self):
        title = Text("top candidates by entropy", font_size=22, color=MUTED)
        title.to_edge(UP, buff=0.55)
        self.play(FadeIn(title), run_time=0.5)

        entries = [
            (1, "Mink",        "1.1927"),
            (2, "Ferret",      "1.1927"),
            (3, "Weasel",      "1.1909"),
            (4, "Sea Otter",   "1.1890"),
            (5, "River Otter", "1.1890"),
        ]

        rows = []
        y_start = 1.6
        row_gap  = 0.78

        for rank, animal, score in entries:
            y = y_start - (rank - 1) * row_gap
            rank_t  = Text(f"#{rank}", font_size=28,
                           color=AMBER_COL if rank == 1 else MUTED)
            name_t  = Text(animal, font_size=32,
                           color=TEXT_COL, weight=BOLD if rank == 1 else NORMAL)
            score_t = Text(score + " bits", font_size=22, color=MUTED)
            rank_t.move_to( LEFT * 4.0 + UP * y)
            name_t.move_to( LEFT * 1.8 + UP * y)
            score_t.move_to(RIGHT * 2.5 + UP * y)
            rows.append(VGroup(rank_t, name_t, score_t))

        sep = Line(LEFT * 5.5, RIGHT * 5.5,
                   color=EDGE_COL, stroke_width=1).next_to(title, DOWN, buff=0.22)
        self.play(Create(sep), run_time=0.4)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.5 if i < len(rows) - 1 else 0.2)

        self.play(rows[0].animate.scale(1.12), run_time=0.3)
        self.play(rows[0].animate.scale(1/1.12), run_time=0.25)

        tie_note = Text("(tied)", font_size=18, color=MUTED)
        tie_note.next_to(rows[1][2], RIGHT, buff=0.22)
        self.play(FadeIn(tie_note, shift=LEFT * 0.1), run_time=0.4)
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 5
# ─────────────────────────────────────────────────────────────────────────────

class Chapter5_01_WorstCase(Scene):
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        big   = ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard"]
        small = ["Bee", "Crab"]

        self.play(
            *[N[n][0].animate.set_fill(ACCENT,    opacity=0.8)
                               .set_stroke(ACCENT,    width=2) for n in big],
            *[N[n][0].animate.set_fill(GREEN_COL, opacity=0.8)
                               .set_stroke(GREEN_COL, width=2) for n in small],
            run_time=0.7,
        )
        ell_big = SurroundingRectangle(
            VGroup(*[N[n][0] for n in big]),
            color=ACCENT, corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )
        self.play(Create(ell_big), run_time=0.6)

        wc_label = Text("worst case = 5", font_size=24, color=RED_COL)
        wc_label.next_to(ell_big, UP, buff=0.18)
        self.play(FadeIn(wc_label, shift=DOWN * 0.1), run_time=0.5)
        self.wait(1.8)

        blue_new  = ["Wolf", "Cat", "Rabbit"]
        green_new = ["Eagle", "Lizard", "Bee", "Crab"]

        new_ell_big = SurroundingRectangle(
            VGroup(*[N[n][0] for n in green_new]),
            color=GREEN_COL, corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )
        new_wc = Text("worst case = 4", font_size=24, color=AMBER_COL)
        new_wc.next_to(new_ell_big, UP, buff=0.18)

        self.play(
            *[N[n][0].animate.set_fill(ACCENT,    opacity=0.8)
                               .set_stroke(ACCENT,    width=2) for n in blue_new],
            *[N[n][0].animate.set_fill(GREEN_COL, opacity=0.8)
                               .set_stroke(GREEN_COL, width=2) for n in green_new],
            Transform(ell_big,  new_ell_big),
            Transform(wc_label, new_wc),
            run_time=1.0,
        )
        self.wait(2.5)


class Chapter5_02_EntropyVsMinmax(Scene):
    """
    Left panel  (Entropy):  step-by-step build:
        p labels → I formulas → decimal values → p·I terms → H sum
    Right panel (Minmax):   only the max bucket matters.
        small cluster dims; brace + "max = 5" appears; then "ignore p" note.

    Both use the 5 vs 2 split as the shared example.
    """

    def construct(self):
        p_big   = 5 / 7
        p_small = 2 / 7
        I_big   = -math.log2(p_big)
        I_small = -math.log2(p_small)
        w_big   = p_big   * I_big
        w_small = p_small * I_small
        H_val   = w_big + w_small

        # ── Shared layout ──────────────────────────────────────────────────
        div = DashedLine(UP * 3.5, DOWN * 3.5, color=EDGE_COL, stroke_width=1.2)
        self.play(Create(div), run_time=0.3)

        def make_split(x_off, title_str, title_color):
            """Build the tree-split diagram for one panel."""
            top    = np.array([x_off,  2.4, 0])
            bl     = np.array([x_off - 1.5, 0.6, 0])
            br     = np.array([x_off + 1.5, 0.6, 0])
            root   = Dot(top, radius=0.11, color=MUTED)
            line_l = Line(top, bl, color=EDGE_COL, stroke_width=2)
            line_r = Line(top, br, color=EDGE_COL, stroke_width=2)

            def cluster(n, color, center):
                return VGroup(*[
                    Circle(radius=0.12, fill_color=color,
                           fill_opacity=1, stroke_width=0)
                    .move_to(center + LEFT * 0.30*(n-1)/2 + RIGHT * 0.30*i)
                    for i in range(n)
                ])

            cl  = cluster(5, ACCENT,    bl)
            cr  = cluster(2, GREEN_COL, br)
            hdr = Text(title_str, font_size=24, color=title_color, weight=BOLD)
            hdr.move_to(top + UP * 0.55)
            return VGroup(root, line_l, line_r, hdr), cl, cr, bl, br

        struct_l, cl_l, cr_l, bl_l, br_l = make_split(-3.2, "Entropy",  ACCENT)
        struct_r, cl_r, cr_r, bl_r, br_r = make_split( 3.2, "Minmax",   AMBER_COL)

        self.play(
            FadeIn(struct_l), FadeIn(cl_l), FadeIn(cr_l),
            FadeIn(struct_r), FadeIn(cl_r), FadeIn(cr_r),
            run_time=0.7,
        )
        self.wait(0.5)

        # ── Entropy side: step-by-step ─────────────────────────────────────

        # Step 1 — probability labels on each branch
        p_lbl_big = MathTex(r"p = \tfrac{5}{7}", font_size=22, color=ACCENT)
        p_lbl_big.next_to(cl_l, DOWN, buff=0.16)

        p_lbl_small = MathTex(r"p = \tfrac{2}{7}", font_size=22, color=GREEN_COL)
        p_lbl_small.next_to(cr_l, DOWN, buff=0.16)

        self.play(FadeIn(p_lbl_big), FadeIn(p_lbl_small), run_time=0.5)
        self.wait(0.6)

        # Step 2 — I = -log2(p) formula for each
        I_formula_big = MathTex(
            r"I = -\log_2\!\bigl(\tfrac{5}{7}\bigr)",
            font_size=17, color=MUTED,
        ).next_to(p_lbl_big, DOWN, buff=0.14)

        I_formula_small = MathTex(
            r"I = -\log_2\!\bigl(\tfrac{2}{7}\bigr)",
            font_size=17, color=MUTED,
        ).next_to(p_lbl_small, DOWN, buff=0.14)

        self.play(FadeIn(I_formula_big), FadeIn(I_formula_small), run_time=0.5)
        self.wait(0.6)

        # Step 3 — decimal values
        I_dec_big = MathTex(rf"\approx {I_big:.2f}", font_size=17, color=MUTED)\
            .next_to(I_formula_big, DOWN, buff=0.10)
        I_dec_small = MathTex(rf"\approx {I_small:.2f}", font_size=17, color=MUTED)\
            .next_to(I_formula_small, DOWN, buff=0.10)

        self.play(FadeIn(I_dec_big), FadeIn(I_dec_small), run_time=0.5)
        self.wait(0.6)

        # Step 4 — weighted terms p·I
        w_lbl_big = MathTex(rf"p \cdot I \approx {w_big:.2f}",
                             font_size=17, color=ACCENT)\
            .next_to(I_dec_big, DOWN, buff=0.14)
        w_lbl_small = MathTex(rf"p \cdot I \approx {w_small:.2f}",
                               font_size=17, color=GREEN_COL)\
            .next_to(I_dec_small, DOWN, buff=0.14)

        self.play(FadeIn(w_lbl_big), FadeIn(w_lbl_small), run_time=0.5)
        self.wait(0.6)

        # Step 5 — H sum at the bottom of the left panel
        H_lbl = MathTex(
            rf"H = {w_big:.2f} + {w_small:.2f} = {H_val:.2f}\ \text{{bits}}",
            font_size=20, color=TEXT_COL,
        )
        H_lbl.move_to(np.array([-3.2, -2.6, 0]))

        self.play(Write(H_lbl), run_time=0.9)
        self.wait(0.8)

        # ── Minmax side: only the max matters ─────────────────────────────

        # Dim the small cluster first
        self.play(cr_r.animate.set_opacity(0.18), run_time=0.5)

        # Brace on the big cluster
        brace = Brace(cl_r, direction=DOWN, color=RED_COL)
        max_lbl = Text("max = 5", font_size=22, color=RED_COL)
        max_lbl.next_to(brace, DOWN, buff=0.12)

        self.play(GrowFromCenter(brace), run_time=0.5)
        self.play(FadeIn(max_lbl), run_time=0.4)
        self.wait(0.8)

        # "probabilities ignored" note to contrast with entropy side
        ignore_note = Text("probabilities don't matter —\njust the size of the biggest bucket",
                           font_size=15, color=MUTED, line_spacing=1.4)
        ignore_note.move_to(np.array([3.2, -2.2, 0]))

        self.play(FadeIn(ignore_note, shift=UP * 0.1), run_time=0.5)
        self.wait(2.5)


class Chapter5_03_Convergence(Scene):
    def construct(self):
        entropy_top = ["Mink", "Ferret", "Weasel", "Sea Otter", "River Otter"]
        minmax_top  = ["Bison", "Water Buffalo", "Dog", "Yak", "Skunk"]

        def make_list(title, items, x_center, title_color):
            title_t = Text(title, font_size=24, color=title_color, weight=BOLD)
            title_t.move_to(np.array([x_center, 2.8, 0]))
            sep = Line(
                np.array([x_center - 2.0, 2.45, 0]),
                np.array([x_center + 2.0, 2.45, 0]),
                color=EDGE_COL, stroke_width=1.2,
            )
            rows = VGroup()
            for i, name in enumerate(items):
                row = Text(f"#{i+1}  {name}", font_size=22, color=TEXT_COL)
                row.move_to(np.array([x_center, 1.8 - i * 0.72, 0]))
                rows.add(row)
            return VGroup(title_t, sep, rows), rows

        panel_e, rows_e = make_list("Entropy", entropy_top, -3.2, ACCENT)
        panel_m, rows_m = make_list("Minmax",  minmax_top,   3.2, AMBER_COL)
        div = DashedLine(UP * 3.2, DOWN * 3.2, color=EDGE_COL, stroke_width=1.2)

        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(panel_e[0]), FadeIn(panel_e[1]),
                  FadeIn(panel_m[0]), FadeIn(panel_m[1]), run_time=0.5)

        for re_, rm_ in zip(panel_e[2], panel_m[2]):
            self.play(
                FadeIn(re_, shift=RIGHT * 0.2),
                FadeIn(rm_, shift=LEFT  * 0.2),
                run_time=0.4,
            )
            self.wait(0.25)

        self.wait(0.8)

        # Dog is #13 by entropy — use as bridge between lists
        dog_row = rows_m[2]
        dog_box = SurroundingRectangle(
            dog_row, color=AMBER_COL,
            corner_radius=0.12, stroke_width=1.8, buff=0.10,
        )
        dog_note = Text("also #13 by entropy", font_size=16, color=AMBER_COL)
        dog_note.next_to(dog_box, RIGHT, buff=0.18)

        self.play(Create(dog_box), run_time=0.4)
        self.play(FadeIn(dog_note, shift=LEFT * 0.1), run_time=0.4)
        self.wait(0.9)

        note = Text("both strategies favor the carnivore zone",
                    font_size=20, color=MUTED)
        note.to_edge(DOWN, buff=0.45)
        note_line = Line(
            np.array([-5.2, note.get_top()[1] + 0.1, 0]),
            np.array([ 5.2, note.get_top()[1] + 0.1, 0]),
            color=MUTED, stroke_width=1,
        )
        self.play(Create(note_line), FadeIn(note), run_time=0.6)
        self.wait(2.5)


class Chapter5_04_MinmaxLeaderboard(Scene):
    def construct(self):
        title = Text("top candidates by minmax simulation", font_size=22, color=MUTED)
        title.to_edge(UP, buff=0.55)
        self.play(FadeIn(title), run_time=0.5)

        entries = [
            (1, "Bison",         "4.78 avg"),
            (2, "Water Buffalo", "4.78 avg"),
            (3, "Dog",           "4.79 avg"),
            (4, "Yak",           "4.79 avg"),
            (5, "Skunk",         "4.80 avg"),
        ]

        rows = []
        y_start = 1.6
        row_gap  = 0.78

        for rank, animal, score in entries:
            y = y_start - (rank - 1) * row_gap
            rank_t  = Text(f"#{rank}", font_size=28,
                           color=AMBER_COL if rank == 1 else MUTED)
            name_t  = Text(animal, font_size=32,
                           color=TEXT_COL, weight=BOLD if rank == 1 else NORMAL)
            score_t = Text(score, font_size=22, color=MUTED)
            rank_t.move_to( LEFT * 4.0 + UP * y)
            name_t.move_to( LEFT * 1.5 + UP * y)
            score_t.move_to(RIGHT * 2.8 + UP * y)
            rows.append(VGroup(rank_t, name_t, score_t))

        sep = Line(LEFT * 5.5, RIGHT * 5.5,
                   color=EDGE_COL, stroke_width=1).next_to(title, DOWN, buff=0.22)
        self.play(Create(sep), run_time=0.4)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.5 if i < len(rows) - 1 else 0.2)

        self.play(rows[0].animate.scale(1.12), run_time=0.3)
        self.play(rows[0].animate.scale(1/1.12), run_time=0.25)

        note = Text("top 50 candidates within 0.05 guesses of each other",
                    font_size=16, color=MUTED)
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 7
# ─────────────────────────────────────────────────────────────────────────────

class Chapter7_01_MinkAnswer(Scene):
    def construct(self):
        answer = Text("Mink", font_size=96, color=TEXT_COL, weight=BOLD)
        underline = Line(
            answer.get_left(), answer.get_right(),
            color=ACCENT, stroke_width=3,
        ).next_to(answer, DOWN, buff=0.14)

        self.play(Write(answer), run_time=1.0)
        self.play(Create(underline), run_time=0.4)
        self.wait(0.8)

        self.play(
            answer.animate.scale(0.52).to_edge(UP, buff=0.6),
            underline.animate.scale(0.52).to_edge(UP, buff=1.05),
            run_time=0.8,
        )

        podium_data = [
            ("#1", "Mink",   "1.1927 bits", AMBER_COL),
            ("#2", "Ferret", "1.1927 bits", MUTED),
            ("#3", "Weasel", "1.1909 bits", MUTED),
        ]

        rows = VGroup()
        for i, (rank, name, score, col) in enumerate(podium_data):
            rank_t  = Text(rank,  font_size=26, color=col)
            name_t  = Text(name,  font_size=30, color=TEXT_COL,
                           weight=BOLD if i == 0 else NORMAL)
            score_t = Text(score, font_size=22, color=MUTED)
            rank_t.move_to( LEFT * 3.8 + DOWN * (0.8 + i * 0.85))
            name_t.move_to( LEFT * 1.5 + DOWN * (0.8 + i * 0.85))
            score_t.move_to(RIGHT * 2.4 + DOWN * (0.8 + i * 0.85))
            rows.add(VGroup(rank_t, name_t, score_t))

        sep = Line(LEFT * 5.3, RIGHT * 5.3,
                   color=EDGE_COL, stroke_width=1).move_to(DOWN * 0.15)
        self.play(Create(sep), run_time=0.3)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.45)
            self.wait(0.3)

        tie = Text("(tied)", font_size=16, color=MUTED)
        tie.next_to(rows[1][2], RIGHT, buff=0.18)
        self.play(FadeIn(tie, shift=LEFT * 0.1), run_time=0.35)
        self.wait(2.5)


class Chapter7_02_BiggerIdea(Scene):
    """
    Three beats:
    1. Cross-fading real-world examples
    2. What the question forced us to build
    3. Final two-line payoff with longer hold
    """
    def construct(self):
        examples = [
            ("Debugging code.",          MUTED),
            ("Medical diagnosis.",        MUTED),
            ("Playing Twenty Questions.", MUTED),
            ("Metazooa.",                 ACCENT),
        ]

        connector = Text("Always the same problem:",
                         font_size=28, color=MUTED).move_to(UP * 1.2)
        subline   = Text("ask questions that split possibilities evenly",
                         font_size=28, color=TEXT_COL).move_to(ORIGIN)

        self.play(FadeIn(connector, shift=UP * 0.15), run_time=0.7)

        prev = None
        for phrase, color in examples:
            t = Text(phrase, font_size=42, color=color, weight=BOLD)
            t.move_to(DOWN * 1.0)
            if prev is None:
                self.play(FadeIn(t, shift=UP * 0.12), run_time=0.6)
            else:
                self.play(FadeOut(prev, shift=UP * 0.1), run_time=0.3)
                self.play(FadeIn(t,    shift=UP * 0.12), run_time=0.5)
            self.wait(1.4)
            prev = t

        self.play(FadeOut(prev), run_time=0.4)
        self.play(FadeIn(subline, shift=UP * 0.15), run_time=0.7)
        self.wait(1.2)
        self.play(FadeOut(VGroup(connector, subline)), run_time=0.5)

        # ── Beat 2: what answering this question required ──────────────────
        build_lines = VGroup(
            Text("To answer one game question,",          font_size=30, color=MUTED),
            Text("we had to formalize uncertainty,",      font_size=30, color=TEXT_COL),
            Text("think geometrically about a tree,",    font_size=30, color=TEXT_COL),
            Text("and ask what's most useful to know next.", font_size=30, color=ACCENT),
        ).arrange(DOWN, buff=0.38).move_to(ORIGIN)

        for line in build_lines:
            self.play(FadeIn(line, shift=UP * 0.12), run_time=0.6)
            self.wait(0.9)

        self.wait(0.8)
        self.play(FadeOut(build_lines), run_time=0.6)

        # ── Beat 3: final payoff ───────────────────────────────────────────
        final = VGroup(
            Text("Measure your uncertainty.", font_size=44,
                 color=TEXT_COL, weight=BOLD),
            Text("Cut it in half.",           font_size=44,
                 color=ACCENT,   weight=BOLD),
        ).arrange(DOWN, buff=0.38).move_to(ORIGIN)

        self.play(FadeIn(final[0], shift=UP * 0.15), run_time=0.7)
        self.wait(0.5)
        self.play(FadeIn(final[1], shift=UP * 0.15), run_time=0.7)
        self.wait(4.0)
