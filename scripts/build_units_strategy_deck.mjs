import path from "node:path";
import { fileURLToPath } from "node:url";
import fsSync from "node:fs";

const artifactToolPath =
  "file:///C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel,
  text,
  image,
  shape,
  rule,
  fill,
  fixed,
  hug,
  grow,
  fr,
  auto,
  wrap,
} = await import(artifactToolPath);

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "output");
const previewDir = path.join(outDir, "unit_strategy_previews");

const W = 1920;
const H = 1080;
const colors = {
  ink: "#172126",
  softInk: "#405158",
  paper: "#F7F0DE",
  parchment: "#FFF8E8",
  red: "#B84737",
  blue: "#2F6FA3",
  brass: "#D8A642",
  green: "#3C8167",
  teal: "#43A99A",
  brown: "#7A553B",
  dark: "#1C2428",
  pale: "#E9D9B8",
  line: "#CBB98E",
};

const units = [
  {
    name: "Commander",
    hp: 150,
    atk: 20,
    move: 2,
    range: 1,
    cost: 1,
    sprite: "commander.png",
    role: "Anchor",
    personality: "Calm field general",
    pitch: "Wins by staying alive, holding tempo, and forcing the enemy to overextend.",
    accent: colors.brass,
  },
  {
    name: "Warrior",
    hp: 100,
    atk: 40,
    move: 2,
    range: 1,
    cost: 2,
    sprite: "warrior.png",
    role: "Frontline",
    personality: "Reliable shield-breaker",
    pitch: "Best when trading cleanly at the edge of a contested lane.",
    accent: colors.brown,
  },
  {
    name: "Archer",
    hp: 80,
    atk: 20,
    move: 2,
    range: 4,
    cost: 2,
    sprite: "archer.png",
    role: "Pressure",
    personality: "Patient lane controller",
    pitch: "Controls space by threatening targets long before melee units arrive.",
    accent: colors.green,
  },
  {
    name: "Healer",
    hp: 80,
    atk: 30,
    move: 3,
    range: 3,
    cost: 2,
    sprite: "healer.png",
    role: "Support",
    personality: "Mercy with a plan",
    pitch: "Turns wounded allies into repeat threats; cannot damage enemies.",
    accent: colors.teal,
  },
  {
    name: "Trebuchet",
    hp: 70,
    atk: 20,
    move: 1,
    range: 99,
    cost: 3,
    sprite: "trebuchet.png",
    role: "Siege",
    personality: "Slow, loud, inevitable",
    pitch: "Punishes clustered enemies with board-wide reach and splash pressure.",
    accent: colors.red,
  },
  {
    name: "Viking",
    hp: 90,
    atk: 60,
    move: 1,
    range: 1,
    cost: 2,
    sprite: "viking.png",
    role: "Burst",
    personality: "All-in closer",
    pitch: "Short reach, enormous hit; needs lanes opened before committing.",
    accent: colors.blue,
  },
];

function spritePath(file) {
  return path.join(root, "sprites", "units", file);
}

const spriteDataUrls = new Map(
  units.map((unit) => {
    const bytes = fsSync.readFileSync(spritePath(unit.sprite));
    return [unit.sprite, `data:image/png;base64,${bytes.toString("base64")}`];
  }),
);

function addSlide(presentation, node) {
  const slide = presentation.slides.add();
  slide.compose(node, {
    frame: { left: 0, top: 0, width: W, height: H },
    baseUnit: 8,
  });
  return slide;
}

function t(value, opts = {}) {
  return text(value, {
    height: hug,
    ...opts,
    style: {
      fontFace: "Aptos",
      color: colors.ink,
      ...opts.style,
    },
  });
}

function statLine(label, value, max, color) {
  const width = Math.max(58, Math.round((value / max) * 260));
  return row({ width: fill, height: fixed(28), gap: 16, align: "center" }, [
    t(label, { width: fixed(76), name: `label-${label}`, style: { fontSize: 18, bold: true, color: colors.softInk } }),
    panel({ width: fixed(270), height: fixed(12), fill: "#E6D5AA", borderRadius: "rounded-full" },
      row({ width: fill, height: fill }, [
        shape({ width: fixed(width), height: fill, fill: color, borderRadius: "rounded-full" }),
      ])),
    t(String(value), { width: fixed(54), name: `value-${label}`, style: { fontSize: 19, bold: true, color } }),
  ]);
}

function unitPortrait(unit, size = 220) {
  return image({
    name: `${unit.name}-sprite`,
    dataUrl: spriteDataUrls.get(unit.sprite),
    contentType: "image/png",
    width: fixed(size),
    height: fixed(size),
    fit: "contain",
    alt: `${unit.name} sprite`,
  });
}

function background(content, tone = colors.paper) {
  return layers({ name: "slide-root", width: fill, height: fill }, [
    shape({ name: "background", width: fill, height: fill, fill: tone }),
    content,
  ]);
}

function titleStack(kicker, title, subtitle, light = false) {
  return column({ name: "title-stack", width: fill, height: hug, gap: 16 }, [
    t(kicker, {
      name: "kicker",
      width: fill,
      style: { fontSize: 22, bold: true, color: light ? colors.brass : colors.red, letterSpacing: 0 },
    }),
    t(title, {
      name: "slide-title",
      width: fill,
      style: { fontSize: 64, bold: true, color: light ? colors.parchment : colors.ink },
    }),
    t(subtitle, {
      name: "subtitle",
      width: fill,
      style: { fontSize: 28, color: light ? "#DDE7DD" : colors.softInk },
    }),
  ]);
}

function rosterCell(unit) {
  return panel(
    {
      name: `${unit.name}-roster-cell`,
      width: fill,
      height: fill,
      fill: colors.parchment,
      line: { color: colors.line, width: 2 },
      borderRadius: 20,
      padding: { x: 26, y: 22 },
    },
    column({ width: fill, height: fill, gap: 9, align: "center" }, [
      unitPortrait(unit, 124),
      t(unit.name, { name: `${unit.name}-name`, width: fill, style: { fontSize: 31, bold: true, color: colors.ink } }),
      t(unit.role, { name: `${unit.name}-role`, width: fill, style: { fontSize: 17, bold: true, color: unit.accent } }),
      row({ width: fill, height: hug, gap: 18, align: "center", justify: "center" }, [
        t(`HP ${unit.hp}`, { name: `${unit.name}-hp`, width: hug, style: { fontSize: 18, bold: true } }),
        t(`ATK ${unit.atk}`, { name: `${unit.name}-atk`, width: hug, style: { fontSize: 18, bold: true } }),
      ]),
      row({ width: fill, height: hug, gap: 18, align: "center", justify: "center" }, [
        t(`Move ${unit.move}`, { name: `${unit.name}-move`, width: hug, style: { fontSize: 16, color: colors.softInk } }),
        t(`Range ${unit.range}`, { name: `${unit.name}-range`, width: hug, style: { fontSize: 16, color: colors.softInk } }),
        t(`Cost ${unit.cost}`, { name: `${unit.name}-cost`, width: hug, style: { fontSize: 16, color: colors.softInk } }),
      ]),
    ]),
  );
}

function personalityPanel(unit) {
  return panel(
    {
      name: `${unit.name}-personality`,
      width: fill,
      height: fill,
      fill: colors.parchment,
      line: { color: unit.accent, width: 4 },
      borderRadius: 18,
      padding: { x: 38, y: 34 },
    },
    row({ width: fill, height: fill, gap: 34, align: "center" }, [
      unitPortrait(unit, 216),
      column({ width: fill, height: hug, gap: 14 }, [
        t(unit.name, { name: `${unit.name}-big-name`, width: fill, style: { fontSize: 52, bold: true } }),
        t(unit.personality, { name: `${unit.name}-personality-line`, width: fill, style: { fontSize: 29, bold: true, color: unit.accent } }),
        t(unit.pitch, { name: `${unit.name}-pitch`, width: fill, style: { fontSize: 24, color: colors.softInk } }),
        column({ width: fill, height: hug, gap: 10 }, [
          statLine("HP", unit.hp, 150, unit.accent),
          statLine("ATK", unit.atk, 60, unit.accent),
          statLine("Move", unit.move, 3, unit.accent),
          statLine("Range", Math.min(unit.range, 6), 6, unit.accent),
        ]),
      ]),
    ]),
  );
}

function coverSlide() {
  return background(
    row({ width: fill, height: fill, padding: { x: 96, y: 76 }, gap: 64, align: "center" }, [
      column({ width: grow(1.05), height: fill, gap: 34, justify: "center" }, [
        t("THE GRIDS PROJECT", { name: "cover-kicker", width: fill, style: { fontSize: 24, bold: true, color: colors.brass } }),
        t("Units with jobs, not just numbers", {
          name: "cover-title",
          width: fill,
          style: { fontSize: 88, bold: true, color: colors.parchment },
        }),
        t("A playable guide to stats, personalities, and the strategic habits that make the roster work together.", {
          name: "cover-subtitle",
          width: wrap(850),
          style: { fontSize: 31, color: "#D8E3D8" },
        }),
        rule({ name: "cover-rule", width: fixed(320), stroke: colors.brass, weight: 6 }),
      ]),
      grid(
        {
          name: "cover-sprite-grid",
          width: grow(0.95),
          height: fixed(760),
          columns: [fr(1), fr(1), fr(1)],
          rows: [fr(1), fr(1)],
          columnGap: 18,
          rowGap: 18,
        },
        units.map((unit) =>
          panel({ name: `cover-${unit.name}`, width: fill, height: fill, fill: "#263135", borderRadius: 24, padding: 18 },
            column({ width: fill, height: fill, align: "center", justify: "center", gap: 6 }, [
              unitPortrait(unit, 178),
              t(unit.name, { width: fill, name: `cover-name-${unit.name}`, style: { fontSize: 18, bold: true, color: colors.parchment } }),
            ])),
        ),
      ),
    ]),
    colors.dark,
  );
}

function rosterSlide() {
  return background(
    column({ width: fill, height: fill, padding: { x: 76, y: 60 }, gap: 36 }, [
      titleStack("ROSTER SNAPSHOT", "Every unit has a sharp tactical job", "Stats define the limits; personality tells you when to commit."),
      grid(
        {
          name: "roster-grid",
          width: fill,
          height: fill,
          columns: [fr(1), fr(1), fr(1)],
          rows: [fr(1), fr(1)],
          columnGap: 24,
          rowGap: 24,
        },
        units.map(rosterCell),
      ),
    ]),
  );
}

function commanderSlide() {
  const commander = units[0];
  return background(
    row({ width: fill, height: fill, padding: { x: 84, y: 70 }, gap: 52, align: "center" }, [
      column({ width: grow(0.82), height: fill, gap: 30, justify: "center" }, [
        titleStack("COMMAND ROLE", "The Commander is the clock", "A commander does not need to top the damage chart. It needs to make every trade expensive."),
        panel({ width: fill, height: hug, fill: "#F1E3BE", borderRadius: 18, padding: { x: 28, y: 24 } },
          t("Personality: patient, stubborn, and politically impossible to ignore.", {
            name: "commander-personality",
            width: fill,
            style: { fontSize: 30, bold: true, color: colors.brown },
          })),
      ]),
      personalityPanel(commander),
    ]),
  );
}

function frontlineSlide() {
  const warrior = units[1];
  const viking = units[5];
  return background(
    column({ width: fill, height: fill, padding: { x: 84, y: 64 }, gap: 38 }, [
      titleStack("FRONTLINE PERSONALITIES", "Warrior holds the door. Viking breaks it.", "Both want melee contact, but they ask for different support."),
      row({ width: fill, height: fill, gap: 36 }, [personalityPanel(warrior), personalityPanel(viking)]),
    ]),
  );
}

function rangedSlide() {
  const archer = units[2];
  const trebuchet = units[4];
  return background(
    column({ width: fill, height: fill, padding: { x: 84, y: 64 }, gap: 38 }, [
      titleStack("RANGED PERSONALITIES", "Archer draws lines. Trebuchet redraws the map.", "Range is not only damage; it is a promise that some squares are unsafe."),
      row({ width: fill, height: fill, gap: 36 }, [personalityPanel(archer), personalityPanel(trebuchet)]),
    ]),
  );
}

function healerSlide() {
  const healer = units[3];
  return background(
    row({ width: fill, height: fill, padding: { x: 84, y: 70 }, gap: 56, align: "center" }, [
      personalityPanel(healer),
      column({ width: grow(0.82), height: fill, gap: 26, justify: "center" }, [
        titleStack("SUPPORT ROLE", "The Healer buys second chances", "Healing is a tempo weapon: it turns one surviving ally into two future attacks."),
        t("Best use: keep the unit that controls the lane alive, not the unit that is easiest to reach.", {
          name: "healer-tip",
          width: wrap(700),
          style: { fontSize: 33, bold: true, color: colors.green },
        }),
      ]),
    ]),
  );
}

function strategyEconomySlide() {
  return background(
    column({ width: fill, height: fill, padding: { x: 92, y: 70 }, gap: 44 }, [
      titleStack("STRATEGY 01", "Spend action points on position before damage", "The game rewards threats that survive to act again."),
      grid(
        { width: fill, height: fill, columns: [fr(1), fr(1), fr(1)], rows: [fr(1)], columnGap: 30 },
        [
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 34, y: 34 } },
            column({ width: fill, height: fill, gap: 20 }, [
              t("1", { name: "economy-step-1-num", width: fill, style: { fontSize: 74, bold: true, color: colors.red } }),
              t("Develop a threat", { name: "economy-step-1-title", width: fill, style: { fontSize: 34, bold: true } }),
              t("Move or deploy so next turn starts with a target already under pressure.", { name: "economy-step-1-body", width: fill, style: { fontSize: 25, color: colors.softInk } }),
            ])),
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 34, y: 34 } },
            column({ width: fill, height: fill, gap: 20 }, [
              t("2", { name: "economy-step-2-num", width: fill, style: { fontSize: 74, bold: true, color: colors.blue } }),
              t("Draw only with intent", { name: "economy-step-2-title", width: fill, style: { fontSize: 34, bold: true } }),
              t("A card draw costs tempo. Draw when the board is stable or your hand lacks the next role.", { name: "economy-step-2-body", width: fill, style: { fontSize: 25, color: colors.softInk } }),
            ])),
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 34, y: 34 } },
            column({ width: fill, height: fill, gap: 20 }, [
              t("3", { name: "economy-step-3-num", width: fill, style: { fontSize: 74, bold: true, color: colors.green } }),
              t("Attack when it changes the map", { name: "economy-step-3-title", width: fill, style: { fontSize: 34, bold: true } }),
              t("Damage matters most when it removes a unit, opens a lane, or forces the commander backward.", { name: "economy-step-3-body", width: fill, style: { fontSize: 25, color: colors.softInk } }),
            ])),
        ],
      ),
    ]),
  );
}

function strategyPositionSlide() {
  return background(
    row({ width: fill, height: fill, padding: { x: 84, y: 70 }, gap: 52, align: "center" }, [
      column({ width: grow(0.9), height: fill, gap: 30, justify: "center" }, [
        titleStack("STRATEGY 02", "Make range bands do the work", "A good formation lets one unit threaten while another unit protects the square it needs."),
        t("Simple formation rule: melee in front, healer one step behind, archer off-angle, trebuchet anywhere it can punish a cluster.", {
          name: "formation-rule",
          width: wrap(790),
          style: { fontSize: 35, bold: true, color: colors.brown },
        }),
      ]),
      panel({ width: grow(1.1), height: fixed(760), fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 20, padding: 28 },
        grid(
          {
            name: "formation-grid",
            width: fill,
            height: fill,
            columns: [fr(1), fr(1), fr(1), fr(1), fr(1)],
            rows: [fr(1), fr(1), fr(1), fr(1)],
            columnGap: 8,
            rowGap: 8,
          },
          Array.from({ length: 20 }).map((_, i) => {
            const map = {
              6: units[1],
              7: units[0],
              11: units[3],
              13: units[2],
              18: units[4],
            };
            const unit = map[i];
            return panel({ width: fill, height: fill, fill: unit ? "#F7E9C8" : "#E9D8AD", line: { color: "#D2BD89", width: 1 }, borderRadius: 8, padding: 8 },
              unit ? unitPortrait(unit, 108) : shape({ width: fill, height: fill, fill: "#E9D8AD" }));
          }),
        )),
    ]),
  );
}

function strategyMatchupsSlide() {
  return background(
    column({ width: fill, height: fill, padding: { x: 92, y: 68 }, gap: 38 }, [
      titleStack("STRATEGY 03", "Win by pairing jobs, not by picking favorites", "The strongest turns combine a mover, a threat, and a closer."),
      grid(
        { width: fill, height: fill, columns: [fr(1), fr(1)], rows: [fr(1), fr(1)], columnGap: 30, rowGap: 26 },
        [
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 30, y: 28 } },
            column({ width: fill, height: fill, gap: 16 }, [
              t("Warrior + Healer", { name: "combo-1-title", width: fill, style: { fontSize: 36, bold: true, color: colors.green } }),
              t("The lane sponge becomes a repeat attacker.", { name: "combo-1-body", width: fill, style: { fontSize: 27, color: colors.softInk } }),
            ])),
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 30, y: 28 } },
            column({ width: fill, height: fill, gap: 16 }, [
              t("Archer + Viking", { name: "combo-2-title", width: fill, style: { fontSize: 36, bold: true, color: colors.blue } }),
              t("Chip from range, then finish with the huge melee hit.", { name: "combo-2-body", width: fill, style: { fontSize: 27, color: colors.softInk } }),
            ])),
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 30, y: 28 } },
            column({ width: fill, height: fill, gap: 16 }, [
              t("Trebuchet + Commander", { name: "combo-3-title", width: fill, style: { fontSize: 36, bold: true, color: colors.red } }),
              t("Make the opponent choose between clustering and walking into command range.", { name: "combo-3-body", width: fill, style: { fontSize: 27, color: colors.softInk } }),
            ])),
          panel({ fill: colors.parchment, line: { color: colors.line, width: 2 }, borderRadius: 18, padding: { x: 30, y: 28 } },
            column({ width: fill, height: fill, gap: 16 }, [
              t("Any threat + knockback", { name: "combo-4-title", width: fill, style: { fontSize: 36, bold: true, color: colors.brown } }),
              t("An attack that moves a unit can open a deployment lane or break a formation.", { name: "combo-4-body", width: fill, style: { fontSize: 27, color: colors.softInk } }),
            ])),
        ],
      ),
    ]),
  );
}

const presentation = Presentation.create({
  slideSize: { width: W, height: H },
});

[
  coverSlide(),
  rosterSlide(),
  commanderSlide(),
  frontlineSlide(),
  rangedSlide(),
  healerSlide(),
  strategyEconomySlide(),
  strategyPositionSlide(),
  strategyMatchupsSlide(),
].forEach((node) => addSlide(presentation, node));

await import("node:fs/promises").then(async (fs) => {
  await fs.mkdir(previewDir, { recursive: true });
  async function saveBlob(blob, filePath) {
    const bytes = Buffer.from(await blob.arrayBuffer());
    await fs.writeFile(filePath, bytes);
  }

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(outDir, "the_grids_units_strategy.pptx"));

  for (let index = 0; index < presentation.slides.count; index += 1) {
    const slide = presentation.slides.getItem(index);
    const png = await slide.export({ format: "png" });
    await saveBlob(png, path.join(previewDir, `slide-${String(index + 1).padStart(2, "0")}.png`));
    const layout = await slide.export({ format: "layout" });
    await saveBlob(layout, path.join(previewDir, `slide-${String(index + 1).padStart(2, "0")}.layout.json`));
  }
});

console.log(`Exported ${path.join(outDir, "the_grids_units_strategy.pptx")}`);
console.log(`Rendered previews in ${previewDir}`);
