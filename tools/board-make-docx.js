// Builds the editable .docx of the board walkthrough.
//
//   python3 tools/board-extract.py for-the-board.html tools/board-blocks.json
//   node    tools/board-make-docx.js . .
//
// The first argument is where board-blocks.json lives, the second is the folder
// the images sit under. Shelby edits the .docx; tools/board-apply-docx.py reads
// her version and writes the wording back into for-the-board.html.

const fs = require('fs');
const path = require('path');
const D = require('docx');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel,
  AlignmentType, BorderStyle, ShadingType, convertInchesToTwip, PageBreak,
  LevelFormat, UnderlineType
} = D;

const ROOT   = process.argv[2] || '/tmp/out';
const BLOCKS = JSON.parse(fs.readFileSync(path.join(ROOT, 'board-blocks.json'), 'utf8'));
const IMGDIR = process.argv[3] || '/tmp/site';
const OUT    = path.join(ROOT, 'CVParkRec_For-the-Board_EDITABLE.docx');

const INK    = '14170F';
const FOREST = '2C4A34';
const SAGE   = '5B5F55';
const PALE   = '8A9285';
const SURF   = 'F4F4F1';

const rule = (before = 200, after = 200) => new Paragraph({
  spacing: { before, after },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'D8D8D0' } },
});

function imgSize(file, maxWIn) {
  // read the intrinsic size out of the JPEG header so nothing is squashed
  const buf = fs.readFileSync(file);
  let i = 2, w = 0, h = 0;
  while (i < buf.length) {
    if (buf[i] !== 0xFF) { i++; continue; }
    const m = buf[i + 1];
    if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC) {
      h = buf.readUInt16BE(i + 5); w = buf.readUInt16BE(i + 7); break;
    }
    i += 2 + buf.readUInt16BE(i + 2);
  }
  if (!w || !h) { w = 1500; h = 940; }
  const wIn = Math.min(maxWIn, w / 150);
  return { width: Math.round(wIn * 96), height: Math.round(wIn * (h / w) * 96) };
}

const kids = [];

// ---------------------------------------------------------------- how to use
kids.push(new Paragraph({
  spacing: { after: 160 },
  shading: { type: ShadingType.CLEAR, fill: SURF },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: FOREST } },
  indent: { left: 200, right: 200 },
  children: [new TextRun({ text: 'How to use this file', bold: true, size: 26, color: INK, font: 'Calibri' })],
}));
[
  'Change any words you like. Type over them the way you would in any document.',
  'Please keep the shape of it. Do not delete a whole heading or paragraph, and do not move sections around. If you want something taken out, leave it where it is and write DELETE at the start of the line instead. If you want something added, write ADD and then what you want, in the spot it should go.',
  'The pictures are here so you can see what sits where. They are screenshots of the real site, so there is nothing to edit on them.',
  'When you are done, save it and tell me. I will read your version, put the changes into the real page and the PDF, and send them back.',
].forEach(t => kids.push(new Paragraph({
  spacing: { after: 120 },
  shading: { type: ShadingType.CLEAR, fill: SURF },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: FOREST } },
  indent: { left: 200, right: 200 },
  children: [new TextRun({ text: t, size: 22, color: SAGE, font: 'Calibri' })],
})));
kids.push(new Paragraph({ children: [new PageBreak()] }));

// ---------------------------------------------------------------- the content
let bylineBuf = [];
function flushByline() {
  if (!bylineBuf.length) return;
  kids.push(new Paragraph({
    spacing: { before: 120, after: 260 },
    children: [new TextRun({ text: bylineBuf.join('   ·   '), size: 20, color: SAGE, font: 'Calibri' })],
  }));
  bylineBuf = [];
}

let dataBuf = {};
function flushData() {
  if (!dataBuf.label) return;
  kids.push(new Paragraph({
    spacing: { after: 60 },
    indent: { left: 240 },
    children: [
      new TextRun({ text: dataBuf.figure + '  ', bold: true, size: 26, color: INK, font: 'Calibri' }),
      new TextRun({ text: dataBuf.label, size: 21, color: INK, font: 'Calibri' }),
      new TextRun({ text: '  —  ' + (dataBuf.note || ''), size: 20, color: SAGE, font: 'Calibri' }),
    ],
  }));
  dataBuf = {};
}

for (const b of BLOCKS) {
  if (b.kind !== 'byline') flushByline();
  if (!['data_label', 'data_figure', 'data_note'].includes(b.kind)) flushData();
  // a second label means the previous cell is finished
  if (b.kind === 'data_label' && dataBuf.label) flushData();

  switch (b.kind) {
    case 'kicker':
      kids.push(new Paragraph({ spacing: { after: 160 }, children: [
        new TextRun({ text: b.text.toUpperCase(), bold: true, size: 17, color: FOREST, characterSpacing: 40, font: 'Calibri' })] }));
      break;

    case 'title':
      kids.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 200 }, children: [
        new TextRun({ text: b.text, bold: true, size: 56, color: INK, font: 'Calibri' })] }));
      break;

    case 'lede':
      kids.push(new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: b.text, size: 26, color: SAGE, font: 'Calibri' })] }));
      break;

    case 'byline': bylineBuf.push(b.text); break;

    case 'eyebrow':
      kids.push(rule(280, 220));
      kids.push(new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun({ text: b.text.toUpperCase(), bold: true, size: 17, color: FOREST, characterSpacing: 40, font: 'Calibri' })] }));
      break;

    case 'h2':
      kids.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 160 }, children: [
        new TextRun({ text: b.text, bold: true, size: 38, color: INK, font: 'Calibri' })] }));
      break;

    case 'h3':
      kids.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 90 }, children: [
        new TextRun({ text: b.text, bold: true, size: 26, color: INK, font: 'Calibri' })] }));
      break;

    case 'lede_p':
      kids.push(new Paragraph({ spacing: { after: 160 }, children: [
        new TextRun({ text: b.text, size: 25, color: SAGE, font: 'Calibri' })] }));
      break;

    case 'p':
    case 'tour_text':
      kids.push(new Paragraph({ spacing: { after: 160 }, children: [
        new TextRun({ text: b.text, size: 23, color: INK, font: 'Calibri' })] }));
      break;

    case 'data_label':  dataBuf.label  = b.text; break;
    case 'data_figure': dataBuf.figure = b.text; break;
    case 'data_note':   dataBuf.note   = b.text; break;

    case 'finding_what':
      kids.push(new Paragraph({ spacing: { before: 150, after: 40 }, children: [
        new TextRun({ text: '•  ', bold: true, size: 23, color: FOREST, font: 'Calibri' }),
        new TextRun({ text: b.text, bold: true, size: 23, color: INK, font: 'Calibri' })] }));
      break;

    case 'finding_why':
      kids.push(new Paragraph({ spacing: { after: 60 }, indent: { left: 300 }, children: [
        new TextRun({ text: b.text, size: 22, color: SAGE, font: 'Calibri' })] }));
      break;

    case 'panel_p':
      kids.push(new Paragraph({
        spacing: { before: 120, after: 120 }, indent: { left: 200, right: 200 },
        shading: { type: ShadingType.CLEAR, fill: SURF },
        children: [new TextRun({ text: b.text, size: 23, color: SAGE, font: 'Calibri' })] }));
      break;

    case 'panel_li':
      kids.push(new Paragraph({
        spacing: { after: 90 }, indent: { left: 460, hanging: 220 },
        shading: { type: ShadingType.CLEAR, fill: SURF },
        children: [
          new TextRun({ text: '•  ', size: 22, color: FOREST, font: 'Calibri' }),
          new TextRun({ text: b.text, size: 22, color: SAGE, font: 'Calibri' })] }));
      break;

    case 'pair_label':
      kids.push(new Paragraph({ spacing: { before: 140, after: 60 }, children: [
        new TextRun({ text: b.text.toUpperCase(), bold: true, size: 17, color: PALE, characterSpacing: 40, font: 'Calibri' })] }));
      break;

    case 'figcaption':
      kids.push(new Paragraph({ spacing: { after: 140 }, children: [
        new TextRun({ text: b.text, size: 20, color: SAGE, italics: true, font: 'Calibri' })] }));
      break;

    case 'image': {
      const f = path.join(IMGDIR, b.src);
      if (!fs.existsSync(f)) { console.log('   missing image', b.src); break; }
      const wide = /phone-/.test(b.src) ? 2.4 : 5.6;
      kids.push(new Paragraph({
        spacing: { before: 80, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new ImageRun({ type: 'jpg', data: fs.readFileSync(f), transformation: imgSize(f, wide) })] }));
      break;
    }

    case 'link':
      kids.push(new Paragraph({ spacing: { before: 140, after: 160 }, children: [
        new TextRun({ text: b.text, bold: true, size: 24, color: FOREST,
                      underline: { type: UnderlineType.SINGLE, color: FOREST }, font: 'Calibri' })] }));
      break;

    case 'sign_name':
      kids.push(rule(260, 200));
      kids.push(new Paragraph({ spacing: { after: 40 }, children: [
        new TextRun({ text: b.text, bold: true, size: 24, color: INK, font: 'Calibri' })] }));
      break;

    case 'sign_line':
      kids.push(new Paragraph({ spacing: { after: 40 }, children: [
        new TextRun({ text: b.text, size: 21, color: SAGE, font: 'Calibri' })] }));
      break;
  }
}
flushByline(); flushData();

const doc = new Document({
  creator: 'Shelby Manzano',
  title: 'A rebuilt website for the District — editable draft',
  description: 'Working copy of the board walkthrough. Edit the words; the page and PDF get rebuilt from it.',
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: convertInchesToTwip(0.85), bottom: convertInchesToTwip(0.85),
                  left: convertInchesToTwip(0.95), right: convertInchesToTwip(0.95) },
      },
    },
    children: kids,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('wrote', OUT, (buf.length / 1024).toFixed(0) + ' KB,', kids.length, 'paragraphs from', BLOCKS.length, 'blocks');
});
