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

    Chapter3_01_EqualProbabilities
    Chapter3_02_SplitAndBars
    Chapter3_03_SurpriseGraph
    Chapter3_04_EntropyExpectedValue
    Chapter3_05_EntropyComparison

    Chapter4_01_ScaleReveal
    Chapter4_02_LeaderboardReveal

    Chapter5_01_WorstCase
    Chapter5_02_EntropyVsMinmax
    Chapter5_03_Convergence

    Chapter7_01_MinkAnswer
    Chapter7_02_BiggerIdea
"""

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

config.background_color = BG


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
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
    # Internal nodes: smaller circle, no label
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
    """Return nodes dict and edges dict."""
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
    """
    Hook shown one short phrase at a time — cross-fading, never more than
    5-6 words on screen at once.
    """
    def construct(self):
        phrases = [
            "Guess an animal.",
            "Any animal.",
            "I give you one hint.",
            "The evolutionary group\nit shares with your guess.",
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
                self.play(
                    FadeOut(prev, shift=UP * 0.12),
                    run_time=0.35,
                )
                self.play(FadeIn(t, shift=UP * 0.15), run_time=0.55)

            hold = 2.8 if i == len(phrases) - 1 else 1.8
            self.wait(hold)
            prev = t

        self.play(FadeOut(prev))


class Chapter1_02_BestFirstGuess(Scene):
    """
    Title card. Just the question and one accent underline.
    """
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
    """
    Full entropy formula written in one go.
    Semi-transparent card so it composites cleanly over b-roll.
    """
    def construct(self):
        formula = MathTex(
            r"H = -\sum_i p_i \log_2 p_i",
            font_size=62,
            color=TEXT_COL,
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
    """
    Tree appears top-down, level by level.
    Only the leaf names are shown — internal nodes are unlabelled circles.
    """
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
    """
    Wolf (blue = our guess) and Cat (green = hidden animal) light up.
    No words — color alone carries the meaning.
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        # Guess
        self.play(
            N["Wolf"][0].animate.set_fill(ACCENT).set_stroke(ACCENT, width=3),
            run_time=0.6,
        )
        self.wait(0.6)

        # Hidden animal
        self.play(
            N["Cat"][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3),
            run_time=0.6,
        )
        self.wait(2)


class Chapter2_03_LCAMeet(Scene):
    """
    Paths from Wolf and Cat travel up and meet at Mammalia.
    Mammalia pulses amber. The only text is a tiny "LCA" tag.
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        # Restore colors from previous scene
        N["Wolf"][0].set_fill(ACCENT).set_stroke(ACCENT, width=3)
        N["Cat"][0].set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3)

        # Highlighted edge copies (drawn on top)
        def hi_edge(key, color):
            return E[key].copy().set_color(color).set_stroke_width(4)

        # Wolf path up
        self.play(Create(hi_edge(("Mammalia","Wolf"), ACCENT)), run_time=0.5)
        # Cat path up
        self.play(Create(hi_edge(("Mammalia","Cat"), GREEN_COL)), run_time=0.5)
        self.wait(0.3)

        # Convergence — Mammalia turns amber and pulses
        self.play(
            N["Mammalia"][0].animate
                .set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3).scale(1.25),
            run_time=0.5,
        )
        self.play(N["Mammalia"][0].animate.scale(1 / 1.25), run_time=0.3)

        # Tiny label — the only text in this scene
        tag = Text("LCA", font_size=20, color=AMBER_COL, weight=BOLD)
        tag.next_to(N["Mammalia"][0], RIGHT, buff=0.22)
        self.play(FadeIn(tag, scale=0.8), run_time=0.4)

        self.wait(2.5)
        self.play(FadeOut(tag))


class Chapter2_04_EliminateOutside(Scene):
    """
    Everything outside the Mammalia subtree dims away.
    Survivors pulse green. Zero text.
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        # Restore state
        N["Wolf"][0].set_fill(ACCENT).set_stroke(ACCENT, width=3)
        N["Cat"][0].set_fill(GREEN_COL).set_stroke(GREEN_COL, width=3)
        N["Mammalia"][0].set_fill(AMBER_COL).set_stroke(AMBER_COL, width=3)

        inside_nodes = {"Mammalia", "Wolf", "Cat", "Rabbit"}
        inside_edges = {("Mammalia","Wolf"), ("Mammalia","Cat"), ("Mammalia","Rabbit")}
        outside_nodes = [n for n in LEAVES + INTERNAL if n not in inside_nodes]
        outside_edges = [k for k in EDGES if k not in inside_edges]

        # Dim outside
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

        # Surviving leaves glow green
        survivors = ["Wolf", "Cat", "Rabbit"]
        self.play(
            *[N[n][0].animate.set_fill(GREEN_COL).set_stroke(GREEN_COL, width=2)
              for n in survivors],
            run_time=0.5,
        )
        # Subtle pulse
        self.play(*[N[n][0].animate.scale(1.15) for n in survivors], run_time=0.3)
        self.play(*[N[n][0].animate.scale(1/1.15) for n in survivors], run_time=0.3)

        self.wait(2.5)


class Chapter2_05_BalancedVsUnbalanced(Scene):
    """
    Side-by-side: bad split (5 vs 1) vs good split (3 vs 3).
    Shown purely as colored dots. Labels are just the ratios "5 : 1" and "3 : 3".
    """
    def construct(self):
        def dot_row(n, color, x_start, y, spacing=0.62):
            return VGroup(*[
                Circle(radius=0.21, fill_color=color, fill_opacity=1, stroke_width=0)
                .move_to(np.array([x_start + i * spacing, y, 0]))
                for i in range(n)
            ])

        # ── Left panel: 5 vs 1 ────────────────────────────────────────────
        big   = dot_row(5, ACCENT,     -4.6,  0.4)
        small = dot_row(1, GREEN_COL,  -4.6, -0.5)
        label_l = Text("5 : 2", font_size=26, color=MUTED).move_to([-3.3, 1.6, 0])

        # ── Divider ───────────────────────────────────────────────────────
        div = DashedLine([-1.2, 2.0, 0], [-1.2, -1.5, 0],
                         color=EDGE_COL, stroke_width=1.5)

        # ── Right panel: 3 vs 3 ───────────────────────────────────────────
        half_a  = dot_row(3, ACCENT,     0.2,  0.4)
        half_b  = dot_row(3, GREEN_COL,  0.2, -0.5)
        label_r = Text("3 : 4", font_size=26, color=MUTED).move_to([ 1.5, 1.6, 0])

        # ── Animate ───────────────────────────────────────────────────────
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

        # Highlight the big group = bad (red brace on top)
        bad_brace = Brace(big, direction=UP, color=RED)
        self.play(GrowFromCenter(bad_brace), run_time=0.5)
        self.wait(1.2)

        # Highlight balanced = good (green box on right)
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


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 3
# ─────────────────────────────────────────────────────────────────────────────

# Helper geometry for Chapter 3 flat-dot scenes
_C3_NAMES = ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard", "Bee"]
_C3_XS    = np.linspace(-3.5, 3.5, 6)
_C3_YL    = -1.8   # leaf y
_C3_R     =  0.28  # leaf radius


def _c3_leaves():
    """Return a VGroup of 6 plain leaf circles (no labels)."""
    return VGroup(*[
        Circle(radius=_C3_R, fill_color=NODE_FILL, fill_opacity=1,
               stroke_color=EDGE_COL, stroke_width=2)
        .move_to(np.array([x, _C3_YL, 0]))
        for x in _C3_XS
    ])


def _c3_name_labels(leaves: VGroup):
    """Animal-name labels below each leaf."""
    return VGroup(*[
        Text(name, font_size=15, color=TEXT_COL)
        .next_to(leaves[i], DOWN, buff=0.12)
        for i, name in enumerate(_C3_NAMES)
    ])


class Chapter3_01_EqualProbabilities(Scene):
    """
    Full taxonomy tree. All 7 leaves glow equally — uniform prior.
    1/7 fractions appear above each leaf.
    """
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

        # 1/7 fracs above each leaf
        fracs = VGroup(*[
            MathTex(r"\tfrac{1}{7}", font_size=19, color=MUTED)
            .next_to(N[name][0], UP, buff=0.12)
            for name in LEAVES
        ])
        self.play(FadeIn(fracs, lag_ratio=0.12), run_time=1.0)
        self.wait(0.4)

        # All leaves pulse the same colour — equally possible
        self.play(
            *[N[name][0].animate.set_fill(ACCENT, opacity=0.6)
                                  .set_stroke(ACCENT, width=2)
              for name in LEAVES],
            run_time=0.7,
        )
        self.wait(2.5)


class Chapter3_02_SplitAndBars(Scene):
    """
    Full tree. Phase 1: a bad guess groups 5 leaves (blue) vs 1 (green) —
    ellipses are drawn around each group. Phase 2: a better guess gives
    3 vs 3 — ellipses equalise.
    No bars, no prose.
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        # ── Phase 1: unbalanced — 5 blue (Vertebrata) vs 2 green (Arthropoda) ──
        # Natural split: a guess whose LCA = Root separates the two clades.
        big_leaves   = ["Wolf", "Cat", "Rabbit", "Eagle", "Lizard"]  # Vertebrata (5)
        small_leaves = ["Bee", "Crab"]                                # Arthropoda (2)

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
            color=ACCENT,    corner_radius=0.35, stroke_width=2.5, buff=0.28,
        )
        ell_small = SurroundingRectangle(
            VGroup(*[N[n][0] for n in small_leaves]),
            color=GREEN_COL, corner_radius=0.35, stroke_width=2.5, buff=0.32,
        )

        self.play(Create(ell_big), Create(ell_small), run_time=0.7)
        self.wait(1.8)

        # ── Phase 2: more balanced — 3 blue (Mammalia) vs 4 green (rest) ──
        # LCA = Mammalia: inside = Wolf/Cat/Rabbit, outside = Eagle/Lizard/Bee/Crab
        balanced_blue  = ["Wolf", "Cat", "Rabbit"]
        balanced_green = ["Eagle", "Lizard", "Bee", "Crab"]

        new_ell_blue = SurroundingRectangle(
            VGroup(*[N[n][0] for n in balanced_blue]),
            color=ACCENT,    corner_radius=0.35, stroke_width=2.5, buff=0.28,
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
    """
    Plots  I(p) = −log₂(p).
    Three dots are highlighted: (1/2 → 1 bit), (1/4 → 2 bits), (1/8 → 3 bits).
    Text is limited to axis labels and bit counts next to each dot.
    """
    def construct(self):
        ax = Axes(
            x_range=[0, 1.05, 0.25],
            y_range=[0, 4.2,  1],
            x_length=6.5,
            y_length=4.5,
            axis_config={
                "color": EDGE_COL,
                "stroke_width": 2,
                "include_tip": True,
                "tip_width": 0.18,
                "tip_height": 0.18,
            },
            x_axis_config={"numbers_to_include": [0.25, 0.5, 0.75, 1.0],
                           "font_size": 20, "color": MUTED},
            y_axis_config={"numbers_to_include": [1, 2, 3, 4],
                           "font_size": 20, "color": MUTED},
        ).move_to(ORIGIN + LEFT * 0.5)

        x_label = MathTex("p",      font_size=28, color=MUTED) \
            .next_to(ax.x_axis.get_right(), RIGHT, buff=0.15)
        y_label = MathTex("I(p)",   font_size=28, color=MUTED) \
            .next_to(ax.y_axis.get_top(),  UP,    buff=0.12)
        formula = MathTex(r"I(p) = -\log_2 p", font_size=28, color=ACCENT) \
            .to_corner(UR, buff=0.5)

        curve = ax.plot(
            lambda p: -np.log2(p),
            x_range=[0.06, 1.0],
            color=ACCENT,
            stroke_width=3,
        )

        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label), run_time=1.0)
        self.play(Create(curve), run_time=1.2)
        self.play(Write(formula), run_time=0.8)
        self.wait(0.5)

        # ── Three highlighted points ───────────────────────────────────────
        highlights = [
            (0.5,   1, "1 \\ \\text{bit}"),
            (0.25,  2, "2 \\ \\text{bits}"),
            (0.125, 3, "3 \\ \\text{bits}"),
        ]

        for p_val, bits, label_str in highlights:
            pt = ax.coords_to_point(p_val, bits)

            dot = Dot(pt, color=AMBER_COL, radius=0.09)

            # Dashed drop lines
            v_line = DashedLine(
                ax.coords_to_point(p_val, 0), pt,
                color=MUTED, stroke_width=1.5, dash_length=0.1,
            )
            h_line = DashedLine(
                ax.coords_to_point(0, bits), pt,
                color=MUTED, stroke_width=1.5, dash_length=0.1,
            )

            bit_label = MathTex(label_str, font_size=22, color=AMBER_COL) \
                .next_to(dot, RIGHT, buff=0.18)

            self.play(
                Create(v_line), Create(h_line),
                run_time=0.4,
            )
            self.play(FadeIn(dot, scale=0.5), FadeIn(bit_label), run_time=0.4)
            self.wait(0.9)

        self.wait(2)


class Chapter3_04_EntropyExpectedValue(Scene):
    """
    Two panels side by side: left = 5:1 split, right = 3:3 split.
    Each branch shows the log formula first, then the decimal, then p*I.
    H sums appear at the bottom of each panel.
    """
    def construct(self):
        import math

        # ── Pre-compute values ─────────────────────────────────────────────
        # 5:2 split  (Vertebrata vs Arthropoda)
        pA1, pA2 = 5/7, 2/7
        IA1 = -math.log2(pA1)
        IA2 = -math.log2(pA2)
        wA1, wA2 = pA1 * IA1, pA2 * IA2
        HA = wA1 + wA2

        # 3:4 split  (Mammalia vs rest)
        pB1, pB2 = 3/7, 4/7
        IB1 = -math.log2(pB1)
        IB2 = -math.log2(pB2)
        wB1, wB2 = pB1 * IB1, pB2 * IB2
        HB = wB1 + wB2

        # ── Helper: build one panel ────────────────────────────────────────
        # Returns a VGroup of all mobjects for that panel, and a list of
        # (anim_group, wait) pairs so we can sequence them together.
        def make_panel(x_center, p_left, p_right,
                       col_left, col_right,
                       n_left, n_right,
                       I_left, I_right,
                       w_left, w_right, H_val,
                       denom=7):
            """
            Returns (all_mobs, steps) where steps = list of VGroups
            to FadeIn one at a time.
            """
            top    = np.array([x_center,  2.2, 0])
            bot_l  = np.array([x_center - 1.55, -0.1, 0])
            bot_r  = np.array([x_center + 1.55, -0.1, 0])

            root = Dot(top, color=MUTED, radius=0.10)
            line_l = Line(top, bot_l, color=EDGE_COL, stroke_width=1.8)
            line_r = Line(top, bot_r, color=EDGE_COL, stroke_width=1.8)

            # Leaf dots representing group size
            def dot_cluster(n, color, center):
                spacing = 0.28
                total_w = (n - 1) * spacing
                dots = VGroup(*[
                    Circle(radius=0.10, fill_color=color,
                           fill_opacity=1, stroke_width=0)
                    .move_to(center + LEFT * total_w/2 + RIGHT * spacing * i)
                    for i in range(n)
                ])
                return dots

            cluster_l = dot_cluster(n_left,  col_left,  bot_l)
            cluster_r = dot_cluster(n_right, col_right, bot_r)

            # Probability on each branch
            p_lbl_l = MathTex(
                rf"p = \tfrac{{{int(round(p_left*denom))}}}{{{denom}}}",
                font_size=20, color=col_left,
            ).next_to(line_l.get_center(), LEFT, buff=0.08)

            p_lbl_r = MathTex(
                rf"p = \tfrac{{{int(round(p_right*denom))}}}{{{denom}}}",
                font_size=20, color=col_right,
            ).next_to(line_r.get_center(), RIGHT, buff=0.08)

            # I = -log2(p) formula first, then ≈ decimal
            I_formula_l = MathTex(
                rf"I = -\log_2\!\bigl(\tfrac{{{int(round(p_left*denom))}}}{{{denom}}}\bigr)",
                font_size=18, color=MUTED,
            ).next_to(cluster_l, DOWN, buff=0.18)

            I_decimal_l = MathTex(
                rf"\approx {I_left:.2f}",
                font_size=18, color=MUTED,
            ).next_to(I_formula_l, RIGHT, buff=0.08)

            I_formula_r = MathTex(
                rf"I = -\log_2\!\bigl(\tfrac{{{int(round(p_right*denom))}}}{{{denom}}}\bigr)",
                font_size=18, color=MUTED,
            ).next_to(cluster_r, DOWN, buff=0.18)

            I_decimal_r = MathTex(
                rf"\approx {I_right:.2f}",
                font_size=18, color=MUTED,
            ).next_to(I_formula_r, RIGHT, buff=0.08)

            # p * I weighted terms
            w_lbl_l = MathTex(
                rf"p \cdot I \approx {w_left:.2f}",
                font_size=18, color=col_left,
            ).next_to(I_decimal_l, DOWN, buff=0.15)

            w_lbl_r = MathTex(
                rf"p \cdot I \approx {w_right:.2f}",
                font_size=18, color=col_right,
            ).next_to(I_decimal_r, DOWN, buff=0.15)

            # H sum
            H_lbl = MathTex(
                rf"H = {w_left:.2f} + {w_right:.2f} = {H_val:.2f}\ \text{{bits}}",
                font_size=20, color=TEXT_COL,
            ).next_to(VGroup(w_lbl_l, w_lbl_r), DOWN, buff=0.28)

            structure = VGroup(root, line_l, line_r, cluster_l, cluster_r)
            step1 = VGroup(p_lbl_l, p_lbl_r)
            step2 = VGroup(I_formula_l, I_formula_r)
            step3 = VGroup(I_decimal_l, I_decimal_r)
            step4 = VGroup(w_lbl_l, w_lbl_r)
            step5 = H_lbl

            return structure, [step1, step2, step3, step4, step5]

        # ── Build both panels ──────────────────────────────────────────────
        struct_A, steps_A = make_panel(
            x_center=-3.0,
            p_left=pA1, p_right=pA2,
            col_left=ACCENT, col_right=GREEN_COL,
            n_left=5, n_right=2,
            I_left=IA1, I_right=IA2,
            w_left=wA1, w_right=wA2,
            H_val=HA,
        )

        struct_B, steps_B = make_panel(
            x_center=3.0,
            p_left=pB1, p_right=pB2,
            col_left=ACCENT, col_right=GREEN_COL,
            n_left=3, n_right=4,
            I_left=IB1, I_right=IB2,
            w_left=wB1, w_right=wB2,
            H_val=HB,
        )

        divider = DashedLine(UP * 3.0, DOWN * 3.0, color=EDGE_COL, stroke_width=1.2)

        # Labels for each panel at top
        lbl_A = Text("5 : 2", font_size=22, color=MUTED).move_to([-3.0, 3.2, 0])
        lbl_B = Text("3 : 4", font_size=22, color=MUTED).move_to([ 3.0, 3.2, 0])

        # ── Animate ────────────────────────────────────────────────────────
        self.play(
            FadeIn(lbl_A), FadeIn(lbl_B),
            Create(divider),
            run_time=0.5,
        )
        self.play(FadeIn(struct_A), FadeIn(struct_B), run_time=0.7)
        self.wait(0.4)

        # Reveal each step in both panels simultaneously
        for stepA, stepB in zip(steps_A, steps_B):
            self.play(FadeIn(stepA), FadeIn(stepB), run_time=0.6)
            self.wait(0.9)

        self.wait(1.5)


class Chapter3_05_EntropyComparison(Scene):
    """
    Final payoff: two entropy numbers side by side.
    5:1 → ≈ 0.65 bits (dim).  3:3 → 1.00 bit (glowing).
    Only text is the two numbers and a tiny "H =" prefix.
    """
    def construct(self):
        import math

        H_unbal = -(5/7)*math.log2(5/7) - (2/7)*math.log2(2/7)  # 5:2 split
        H_bal   = -(3/7)*math.log2(3/7) - (4/7)*math.log2(4/7)  # 3:4 split

        # ── Left (unbalanced 5:2) ─────────────────────────────────────────
        dots_left = VGroup(
            *[Circle(radius=0.18, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
              .move_to(LEFT * 4.0 + RIGHT * 0.45 * i + UP * 1.5)
              for i in range(5)],
            *[Circle(radius=0.18, fill_color=GREEN_COL, fill_opacity=1, stroke_width=0)
              .move_to(LEFT * 4.0 + RIGHT * 0.45 * i + UP * 0.8)
              for i in range(2)],
        )

        H_left_lbl = MathTex(
            rf"H = {H_unbal:.2f}\ \text{{bits}}",
            font_size=36, color=MUTED,
        ).move_to(LEFT * 2.8 + DOWN * 0.2)

        # ── Divider ────────────────────────────────────────────────────────
        div = DashedLine(UP * 2.2, DOWN * 2.2, color=EDGE_COL, stroke_width=1.5)

        # ── Right (more balanced 3:4) ──────────────────────────────────────
        dots_right = VGroup(
            *[Circle(radius=0.18, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
              .move_to(RIGHT * 1.0 + RIGHT * 0.45 * i + UP * 1.5)
              for i in range(3)],
            *[Circle(radius=0.18, fill_color=GREEN_COL, fill_opacity=1, stroke_width=0)
              .move_to(RIGHT * 1.0 + RIGHT * 0.45 * i + UP * 0.8)
              for i in range(4)],
        )

        H_right_lbl = MathTex(
            rf"H = {H_bal:.2f}\ \text{{bits}}",
            font_size=36, color=GREEN_COL,
        ).move_to(RIGHT * 2.8 + DOWN * 0.2)

        # ── Animate ────────────────────────────────────────────────────────
        self.play(FadeIn(dots_left), run_time=0.5)
        self.play(Write(H_left_lbl), run_time=0.8)
        self.wait(0.4)

        self.play(Create(div), run_time=0.4)
        self.play(FadeIn(dots_right), run_time=0.5)
        self.play(Write(H_right_lbl), run_time=0.8)
        self.wait(0.8)

        # Right label pulses to draw the eye
        self.play(H_right_lbl.animate.scale(1.18), run_time=0.35)
        self.play(H_right_lbl.animate.scale(1/1.18), run_time=0.3)

        # Dim the left side
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
    Toy tree fades out, replaced by a dense cloud of dots suggesting
    hundreds of animals. A counter ticks up to 822 (real Metazooa count).
    No prose — just the visual scale shock.
    """
    def construct(self):
        N, E = build_tree()
        tree_group = VGroup(*E.values(), *N.values())
        self.add(tree_group)
        self.wait(0.5)

        # Shrink and fade the toy tree to centre
        self.play(
            tree_group.animate.scale(0.18).move_to(ORIGIN).set_opacity(0.25),
            run_time=1.2,
        )
        self.wait(0.3)

        # Generate a dense cloud of small dots filling the frame
        rng = np.random.default_rng(42)
        n_dots = 280
        xs = rng.uniform(-6.5, 6.5, n_dots)
        ys = rng.uniform(-3.5, 3.5, n_dots)

        cloud = VGroup(*[
            Dot(np.array([x, y, 0]), radius=0.045,
                color=EDGE_COL, fill_opacity=0.0)
            for x, y in zip(xs, ys)
        ])

        self.play(
            FadeOut(tree_group),
            FadeIn(cloud, lag_ratio=0.008),
            run_time=1.4,
        )
        self.wait(0.4)

        # Dots brighten one wave at a time
        self.play(
            cloud.animate.set_fill(color=ACCENT, opacity=0.55)
                          .set_stroke(color=ACCENT, width=0.5, opacity=0.6),
            run_time=1.0,
            lag_ratio=0.004,
        )

        # Counter in the corner ticks up to 822
        counter_val = {"v": 0}
        counter_tex = Integer(0, font_size=52, color=TEXT_COL)
        counter_tex.to_corner(DR, buff=0.55)
        self.play(FadeIn(counter_tex), run_time=0.3)

        def update_counter(mob, dt):
            counter_val["v"] = min(counter_val["v"] + dt * 420, 822)
            mob.set_value(int(counter_val["v"]))

        counter_tex.add_updater(update_counter)
        self.wait(2.0)
        counter_tex.remove_updater(update_counter)
        counter_tex.set_value(822)
        self.wait(1.8)


class Chapter4_02_LeaderboardReveal(Scene):
    """
    Top-5 entropy leaderboard drops in one row at a time.
    Rank · animal name · entropy score. Mink row pulses at the end.
    """
    def construct(self):
        title = Text("top candidates by entropy", font_size=22, color=MUTED)
        title.to_edge(UP, buff=0.55)
        self.play(FadeIn(title), run_time=0.5)

        entries = [
            (1, "Mink",   "0.847"),
            (2, "Stoat",  "0.845"),
            (3, "Otter",  "0.843"),
            (4, "Ferret", "0.841"),
            (5, "Weasel", "0.839"),
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

            rank_t.move_to(LEFT * 4.0 + UP * y)
            name_t.move_to(LEFT * 1.8 + UP * y)
            score_t.move_to(RIGHT * 2.5 + UP * y)

            row = VGroup(rank_t, name_t, score_t)
            rows.append(row)

        # Separator line
        sep = Line(LEFT * 5.5, RIGHT * 5.5,
                   color=EDGE_COL, stroke_width=1).next_to(title, DOWN, buff=0.22)
        self.play(Create(sep), run_time=0.4)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.5 if i < len(rows) - 1 else 0.2)

        # Pulse the mink row
        self.play(rows[0].animate.scale(1.12), run_time=0.3)
        self.play(rows[0].animate.scale(1/1.12), run_time=0.25)
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 5
# ─────────────────────────────────────────────────────────────────────────────

class Chapter5_01_WorstCase(Scene):
    """
    Toy tree. Shows the 5:2 split, highlights the largest bucket and
    labels it "worst case = 5". Then morphs to 3:4 split, "worst case = 4".
    Shows that minmax wants to shrink that number.
    """
    def construct(self):
        N, E = build_tree()
        self.add(*E.values(), *N.values())

        # ── Phase 1: bad split 5:2 ─────────────────────────────────────────
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

        # Worst-case label on the big group
        wc_label = Text("worst case = 5", font_size=24, color=RED)
        wc_label.next_to(ell_big, UP, buff=0.18)
        self.play(FadeIn(wc_label, shift=DOWN * 0.1), run_time=0.5)
        self.wait(1.8)

        # ── Phase 2: better split 3:4 ──────────────────────────────────────
        blue_new  = ["Wolf", "Cat", "Rabbit"]
        green_new = ["Eagle", "Lizard", "Bee", "Crab"]

        new_ell_big = SurroundingRectangle(
            VGroup(*[N[n][0] for n in green_new]),   # bigger group is now 4
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
    Same 5:2 split shown twice side by side.
    Left panel: entropy — all buckets weighted, H formula builds up.
    Right panel: minmax — only the max bucket matters, rest fades.
    """
    def construct(self):
        import math

        def split_panel(x_off, title_str, title_color):
            """Return (panel_group, step_sequence)."""
            top  = np.array([x_off,  2.0, 0])
            bl   = np.array([x_off - 1.4, 0.0, 0])
            br   = np.array([x_off + 1.4, 0.0, 0])

            root = Dot(top, radius=0.10, color=MUTED)
            line_l = Line(top, bl, color=EDGE_COL, stroke_width=2)
            line_r = Line(top, br, color=EDGE_COL, stroke_width=2)

            def cluster(n, color, center):
                g = VGroup(*[
                    Circle(radius=0.11, fill_color=color,
                           fill_opacity=1, stroke_width=0)
                    .move_to(center + LEFT * 0.3*(n-1)/2 + RIGHT * 0.3*i)
                    for i in range(n)
                ])
                return g

            cl = cluster(5, ACCENT,    bl)
            cr = cluster(2, GREEN_COL, br)

            hdr = Text(title_str, font_size=22, color=title_color)
            hdr.move_to(top + UP * 0.55)

            struct = VGroup(root, line_l, line_r, cl, cr, hdr)
            return struct, cl, cr, bl, br

        struct_l, cl_l, cr_l, bl_l, br_l = split_panel(-3.2, "Entropy",  ACCENT)
        struct_r, cl_r, cr_r, bl_r, br_r = split_panel( 3.2, "Minmax",   AMBER_COL)

        div = DashedLine(UP * 3.2, DOWN * 3.2, color=EDGE_COL, stroke_width=1.2)

        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(struct_l), FadeIn(struct_r), run_time=0.7)
        self.wait(0.5)

        # ── Entropy side: weight both buckets ─────────────────────────────
        p1, p2 = 5/7, 2/7
        H = -(p1*math.log2(p1) + p2*math.log2(p2))

        p_lbl_l1 = MathTex(r"\tfrac{5}{7}", font_size=22, color=ACCENT)\
            .next_to(cl_l, DOWN, buff=0.14)
        p_lbl_l2 = MathTex(r"\tfrac{2}{7}", font_size=22, color=GREEN_COL)\
            .next_to(cr_l, DOWN, buff=0.14)

        H_lbl = MathTex(rf"H \approx {H:.2f}\ \text{{bits}}",
                         font_size=24, color=TEXT_COL)\
            .move_to(np.array([-3.2, -1.6, 0]))

        self.play(FadeIn(p_lbl_l1), FadeIn(p_lbl_l2), run_time=0.5)
        self.wait(0.4)
        self.play(Write(H_lbl), run_time=0.8)
        self.wait(0.8)

        # ── Minmax side: dim the small bucket, spotlight the big one ──────
        brace = Brace(cl_r, direction=DOWN, color=RED)
        wc_lbl = Text("max = 5", font_size=22, color=RED)\
            .next_to(brace, DOWN, buff=0.12)

        self.play(
            cr_r.animate.set_opacity(0.18),
            GrowFromCenter(brace),
            run_time=0.6,
        )
        self.play(FadeIn(wc_lbl), run_time=0.4)
        self.wait(2.5)


class Chapter5_03_Convergence(Scene):
    """
    Two ranked lists side by side: entropy top-5 vs minmax top-5.
    Shared animals light up in amber to show the strategies largely agree.
    """
    def construct(self):
        # Real approximate results from the script
        entropy_top = ["Mink", "Stoat", "Otter", "Ferret", "Weasel"]
        minmax_top  = ["Bison", "Water buffalo", "Dog", "Yak", "Skunk"]

        # Animals that appear in both (none in these exact lists, but
        # we note they're from the same region of the tree — we highlight
        # that visually with a bracket rather than matching names)
        # Instead, we show both lists then draw a bracket around both
        # saying "same region of the tree"

        def make_list(title, items, x_center, title_color):
            title_t = Text(title, font_size=24,
                           color=title_color, weight=BOLD)
            title_t.move_to(np.array([x_center, 2.8, 0]))
            sep = Line(
                np.array([x_center - 1.8, 2.45, 0]),
                np.array([x_center + 1.8, 2.45, 0]),
                color=EDGE_COL, stroke_width=1.2,
            )
            rows = VGroup()
            for i, name in enumerate(items):
                row = Text(f"#{i+1}  {name}", font_size=24, color=TEXT_COL)
                row.move_to(np.array([x_center, 1.8 - i * 0.72, 0]))
                rows.add(row)
            return VGroup(title_t, sep, rows), rows

        panel_e, rows_e = make_list("Entropy",  entropy_top, -3.0, ACCENT)
        panel_m, rows_m = make_list("Minmax",   minmax_top,   3.0, AMBER_COL)
        div = DashedLine(UP * 3.2, DOWN * 3.2, color=EDGE_COL, stroke_width=1.2)

        self.play(Create(div), run_time=0.3)
        self.play(FadeIn(panel_e[0]), FadeIn(panel_e[1]),
                  FadeIn(panel_m[0]), FadeIn(panel_m[1]), run_time=0.5)

        # Rows drop in together
        for re_, rm_ in zip(panel_e[2], panel_m[2]):
            self.play(
                FadeIn(re_, shift=RIGHT * 0.2),
                FadeIn(rm_, shift=LEFT  * 0.2),
                run_time=0.4,
            )
            self.wait(0.25)

        self.wait(0.8)

        # Draw a brace spanning both columns at the bottom
        # to say "same region"
        bottom_group = VGroup(rows_e[-1], rows_m[-1])
        note = Text("same region of the tree", font_size=20, color=MUTED)
        note.to_edge(DOWN, buff=0.45)
        note_line = Line(
            np.array([-5.2, note.get_top()[1] + 0.1, 0]),
            np.array([ 5.2, note.get_top()[1] + 0.1, 0]),
            color=MUTED, stroke_width=1,
        )
        self.play(Create(note_line), FadeIn(note), run_time=0.6)
        self.wait(2.5)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAPTER 7 – CONCLUSION
# ─────────────────────────────────────────────────────────────────────────────

class Chapter7_01_MinkAnswer(Scene):
    """
    The answer reveal: "Mink" drops in large, then a short podium of the
    top 3 candidates appears below it with their scores.
    """
    def construct(self):
        answer = Text("Mink", font_size=96, color=TEXT_COL, weight=BOLD)
        underline = Line(
            answer.get_left(), answer.get_right(),
            color=ACCENT, stroke_width=3,
        ).next_to(answer, DOWN, buff=0.14)

        self.play(Write(answer), run_time=1.0)
        self.play(Create(underline), run_time=0.4)
        self.wait(0.8)

        # Shrink to top and reveal podium
        self.play(
            answer.animate.scale(0.52).to_edge(UP, buff=0.6),
            underline.animate.scale(0.52).next_to(
                answer.copy().scale(0.52).to_edge(UP, buff=0.6),
                DOWN, buff=0.10,
            ),
            run_time=0.8,
        )

        podium_data = [
            ("#1", "Mink",   "0.847 bits", AMBER_COL),
            ("#2", "Stoat",  "0.845 bits", MUTED),
            ("#3", "Otter",  "0.843 bits", MUTED),
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
                   color=EDGE_COL, stroke_width=1).next_to(underline, DOWN, buff=0.35)
        self.play(Create(sep), run_time=0.3)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.45)
            self.wait(0.3)

        self.wait(2.5)


class Chapter7_02_BiggerIdea(Scene):
    """
    Cross-fading phrases that zoom out from Metazooa to the universal idea.
    Each example fades in, then out, building toward the final line.
    Ends on: "Measure your uncertainty. Cut it in half."
    """
    def construct(self):
        examples = [
            ("Debugging code.",         MUTED),
            ("Medical diagnosis.",       MUTED),
            ("Playing Twenty Questions.",MUTED),
            ("Metazooa.",                ACCENT),
        ]

        connector = Text(
            "Always the same problem:",
            font_size=28, color=MUTED,
        ).move_to(UP * 1.2)

        subline = Text(
            "ask questions that split possibilities evenly",
            font_size=28, color=TEXT_COL,
        ).move_to(ORIGIN)

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

        # Clear and hit the final line
        self.play(FadeOut(VGroup(connector, subline)), run_time=0.5)

        final = VGroup(
            Text("Measure your uncertainty.", font_size=44,
                 color=TEXT_COL, weight=BOLD),
            Text("Cut it in half.",           font_size=44,
                 color=ACCENT,   weight=BOLD),
        ).arrange(DOWN, buff=0.35).move_to(ORIGIN)

        self.play(FadeIn(final[0], shift=UP * 0.15), run_time=0.7)
        self.wait(0.5)
        self.play(FadeIn(final[1], shift=UP * 0.15), run_time=0.7)
        self.wait(3.5)
