const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("C:/Users/ryoko/.npm-global/node_modules/agent-browser/node_modules/playwright-core");

const projectRoot = path.resolve(__dirname, "..");
const outputDir = path.join(projectRoot, "paper", "figures");
const appUrl = process.env.TOPODIALOGUE_URL || "http://localhost:4173/";

const figures = [
  {
    caseName: "spiral-revisit",
    heightMode: "revisitHeight",
    fileName: "fig01-spiral-revisit.png",
    expectedShape: "spiral-like productive revisit",
  },
  {
    caseName: "assistant-induced-loop",
    heightMode: "revisitHeight",
    fileName: "fig02-assistant-induced-loop.png",
    expectedShape: "closed loop",
  },
  {
    caseName: "spiral-escape",
    heightMode: "revisitHeight",
    fileName: "fig03-user-originated-escape.png",
    expectedShape: "escape",
  },
  {
    caseName: "speaker-drift",
    heightMode: "alternativeZ",
    fileName: "fig04-speaker-drift-artifact.png",
    expectedShape: "closed loop",
  },
];

const paperCss = `
  body { background: #070a10 !important; }
  .shell { width: min(1760px, 96vw) !important; max-width: none !important; }
  .dropzone, .load-status, .explorer-controls, footer { display: none !important; }
  .topbar { margin-bottom: 14px !important; }
  .topbar .sub { max-width: 960px !important; }
  .research-controls { margin-bottom: 12px !important; }
  .metrics { grid-template-columns: repeat(8, minmax(120px, 1fr)) !important; }
  .metric { min-height: 72px !important; }
  .workspace { grid-template-columns: minmax(0, 1.55fr) minmax(360px, .75fr) !important; }
  .viewport-card, .inspector { min-height: 660px !important; }
  #viewport { min-height: 610px !important; }
  .research-summary { grid-template-columns: 1.25fr .75fr !important; }
`;

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    args: [
      "--use-angle=swiftshader",
      "--enable-webgl",
      "--enable-unsafe-swiftshader",
      "--ignore-gpu-blocklist",
    ],
  });

  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } });
    await page.goto(appUrl, { waitUntil: "networkidle" });
    await page.addStyleTag({ content: paperCss });

    for (const figure of figures) {
      await page.locator("#synthetic-case").selectOption(figure.caseName);
      await page.locator("#height-mode").selectOption(figure.heightMode);
      await page.locator("#projection-seed").fill("1729");
      await page.locator("#load-synthetic").click();
      await page.locator("#metrics").getByText(figure.expectedShape, { exact: true }).waitFor();
      await page.locator("#reset-view").click();
      await page.waitForTimeout(250);

      const outputPath = path.join(outputDir, figure.fileName);
      await page.screenshot({ path: outputPath, fullPage: true });

      const shape = await page.locator("#metrics .shape-pill").innerText();
      const source = await page.locator("#source-name").innerText();
      console.log(`${figure.fileName}\t${shape}\t${source}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
