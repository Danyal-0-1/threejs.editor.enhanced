/* ============================================================================
 * strata_runner.js — paste into the browser console on the Strata editor page.
 *
 * WHAT IT DOES
 *   For the model that is CURRENTLY LOADED, runs evalEditMatrix() for both
 *   conditions ('scaffolded' and 'bare'), N times each, normalizes whatever the
 *   harness returns into flat rows, and downloads a CSV.
 *
 * WHY N TIMES
 *   Handover doc §4: small models are nondeterministic. One run is an anecdote.
 *   Repeat runs give you a mean and a spread, so you can say whether a cliff is
 *   real or noise.
 *
 * HOW TO USE
 *   1. Load a model in the shell header (select → Load AI). Wait until ready.
 *   2. Paste this whole file into the console. Press Enter.
 *   3. Run:   await strataRun({ model: 'Qwen2.5-Coder-1.5B-Instruct-q4f16_1-MLC', runs: 3 })
 *      (use the EXACT model id + quant string you loaded — it goes in the CSV)
 *   4. A CSV downloads. Repeat for each model × each quant (q4f16_1, q4f32_1).
 *   5. Put all the CSVs in one folder and run plot_matrix.py on it.
 *
 * FIRST TIME: run  await strataProbe()  to print the raw shape evalEditMatrix
 * returns. If the normalizer below doesn't match it, adjust ROW_EXTRACTORS.
 * ========================================================================== */

(() => {
  const TASKS = ['op-type', 'selector', 'arg-extract', 'labeling', 'multi-op'];

  /* Look up evalEditMatrix wherever the app exposes it. */
  function findEval() {
    const c = [
      globalThis.evalEditMatrix,
      globalThis.editor?.evalEditMatrix,
      globalThis.strata?.evalEditMatrix,
    ].find(f => typeof f === 'function');
    if (!c) throw new Error(
      'evalEditMatrix not found on window/editor/strata. ' +
      'Check the release for its actual export name, then edit findEval().');
    return c;
  }

  /* Print the raw return shape so you can verify the normalizer. */
  globalThis.strataProbe = async (condition = 'scaffolded') => {
    const raw = await findEval()(condition);
    console.log('RAW RESULT SHAPE:', raw);
    console.log('JSON:', JSON.stringify(raw, null, 2).slice(0, 2000));
    return raw;
  };

  /* Normalize several plausible shapes into {task: passRate}.
   * Handles:  {'op-type': 0.8, ...}
   *           {results: {'op-type': {passRate: 0.8}}}
   *           [{task:'op-type', pass:4, total:5}, ...]
   */
  function normalize(raw) {
    const out = {};
    if (Array.isArray(raw)) {
      for (const r of raw) {
        const t = r.task ?? r.name;
        if (!t) continue;
        out[t] = r.passRate ?? r.score ??
                 (r.total ? (r.pass ?? r.correct) / r.total : undefined);
      }
      return out;
    }
    const src = raw?.results ?? raw?.tasks ?? raw;
    for (const [k, v] of Object.entries(src || {})) {
      if (typeof v === 'number') out[k] = v;
      else if (v && typeof v === 'object') {
        out[k] = v.passRate ?? v.score ??
                 (v.total ? (v.pass ?? v.correct) / v.total : undefined);
      }
    }
    return out;
  }

  /* Main driver. */
  globalThis.strataRun = async ({ model, runs = 3, conditions = ['scaffolded', 'bare'] } = {}) => {
    if (!model) throw new Error("pass a model id, e.g. strataRun({model:'...q4f16_1-MLC'})");
    const fn = findEval();
    const rows = [];

    for (const condition of conditions) {
      for (let run = 0; run < runs; run++) {
        const t0 = performance.now();
        let scores = {}, error = '';
        try {
          scores = normalize(await fn(condition));
        } catch (e) {
          error = String(e?.message || e);
          console.error(`[${condition} run${run}] FAILED:`, e);
        }
        const secs = ((performance.now() - t0) / 1000).toFixed(1);
        for (const task of TASKS) {
          rows.push({
            model, condition, run, task,
            score: scores[task] ?? '',
            seconds: secs, error,
          });
        }
        console.log(`[${model}] ${condition} run${run} (${secs}s)`,
                    TASKS.map(t => `${t}=${(scores[t] ?? NaN).toFixed?.(2) ?? '?'}`).join(' '));
      }
    }

    /* CSV download */
    const cols = ['model', 'condition', 'run', 'task', 'score', 'seconds', 'error'];
    const csv = [cols.join(',')].concat(
      rows.map(r => cols.map(c => `"${String(r[c]).replace(/"/g, '""')}"`).join(','))
    ).join('\n');
    const safe = model.replace(/[^A-Za-z0-9._-]/g, '_');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = `strata_${safe}.csv`;
    a.click();

    console.table(rows.filter(r => r.run === 0));
    console.log(`✅ downloaded strata_${safe}.csv  (${rows.length} rows)`);
    return rows;
  };

  console.log('strata_runner ready.\n' +
    "  await strataProbe()                       ← check the harness return shape first\n" +
    "  await strataRun({model:'<id>', runs:3})   ← run the matrix for the loaded model");
})();
