const text = `Here's your current leave balance for 2026:
\`\`\`ui-card
{
    "status": ["Analyzing...", "Intent: Check leave balance", "Fetching records..."],
    "title": "Leave Balance",
    "primary_value": "6 days",
    "primary_label": "of Annual Leave remaining",
    "warning": "You have a total of 9 Medical Leave days remaining.",
    "breakdown": [
        {"label": "Annual Leave", "value": "6 days"},
        {"label": "Medical Leave", "value": "9 days"},
        {"label": "Unpaid Leave", "value": "0 days"}
    ]
}
\`\`\`
If you need any further assistance or want to apply for leave, just let me know! 😊`;

function renderComplexCard(jsonStr) {
    try {
        let data;
        try {
            data = JSON.parse(jsonStr);
        } catch (e) {
            data = (new Function("return " + jsonStr))();
        }

        console.log("SUCCESSFULLY PARSED JSON DATA!");
        return `<div class="complex-data-card">DONE</div>`;
    } catch (e) {
        console.log("FAILED TO PARSE IN RENDERCOMPLEXCARD:", e.message);
        return jsonStr;
    }
}

let html = text;
let searchStart = 0;
while (true) {
    let keywordIdx = html.indexOf('"status":', searchStart);
    if (keywordIdx === -1) keywordIdx = html.indexOf('"title":', searchStart);
    if (keywordIdx === -1) break;

    let openIdx = -1;
    for (let i = keywordIdx; i >= 0; i--) {
        if (html[i] === '{') {
            openIdx = i;
            break;
        }
    }

    let openBraces = 0;
    let endIndex = -1;
    let inString = false;
    let escapeNext = false;

    for (let i = openIdx; i < html.length; i++) {
        let char = html[i];

        if (escapeNext) {
            escapeNext = false;
            continue;
        }
        if (char === '\\') {
            escapeNext = true;
            continue;
        }
        if (char === '"') {
            inString = !inString;
        }

        if (!inString) {
            if (char === '{') openBraces++;
            if (char === '}') openBraces--;

            if (openBraces === 0) {
                endIndex = i;
                break;
            }
        }
    }

    if (endIndex !== -1) {
        let extractStr = html.substring(openIdx, endIndex + 1);
        console.log("==== EXTRACTED STRING ====");
        console.log(extractStr);
        console.log("==========================");

        let parsedCard = renderComplexCard(extractStr);

        let replaceStart = openIdx;
        while (replaceStart > 0 && (html[replaceStart - 1] === '\`' || html[replaceStart - 1] === '\n' || html[replaceStart - 1] === ' ')) {
            replaceStart--;
        }
        if (replaceStart >= 7 && html.substring(replaceStart - 7, replaceStart) === 'ui-card') replaceStart -= 7;
        if (replaceStart >= 4 && html.substring(replaceStart - 4, replaceStart) === '\`\`\`\n') replaceStart -= 4;
        if (replaceStart >= 3 && html.substring(replaceStart - 3, replaceStart) === '\`\`\`') replaceStart -= 3;

        let replaceEnd = endIndex + 1;
        while (replaceEnd < html.length && (html[replaceEnd] === '\`' || html[replaceEnd] === '\n' || html[replaceEnd] === ' ')) {
            replaceEnd++;
        }

        html = html.substring(0, replaceStart) + parsedCard + html.substring(replaceEnd);
        searchStart = replaceStart + parsedCard.length;
    } else {
        searchStart = keywordIdx + 1;
    }
}

console.log("FINAL HTML:");
console.log(html);
