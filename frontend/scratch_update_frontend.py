import os

file_path = r"d:\UIT\Research\Viettel\frontend\src\components\PageIdealTuning.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    # 1. Colors in ConvergenceChart
    """    const colors = {
        'GA': '#3b82f6',
        'PSO': '#10b981',
        'BO': '#ec4899'
    };""": """    const colors = {
        'GA': '#3b82f6',
        'PSO': '#10b981',
        'TPE': '#ec4899',
        'CMA-ES': '#8b5cf6',
        'GWO': '#f59e0b'
    };""",
    
    # 2. forEach in ConvergenceChart
    "['GA', 'PSO', 'BO'].forEach(alg => {": "['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO'].forEach(alg => {",
    
    # 3. itersInput
    'const [itersInput, setItersInput] = useState({ GA: "10, 20", PSO: "10, 20", BO: "10, 20" });': 'const [itersInput, setItersInput] = useState({ GA: "10, 20", PSO: "10, 20", TPE: "10, 20", "CMA-ES": "10, 20", GWO: "10, 20" });',
    
    # 4. visiblePlots
    'const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: false, BO: false, Target: true });': 'const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: false, TPE: false, "CMA-ES": false, GWO: false, Target: true });',
    
    # 5. for..of loops
    "for (const alg of ['GA', 'PSO', 'BO']) {": "for (const alg of ['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO']) {",
    
    # 6. map in ui
    "{['GA', 'PSO', 'BO'].map(alg => (": "{['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO'].map(alg => (",
    
    # 7. newTuned
    """                if (fullResults.PSO?.best_overall) newTuned.PSO = fullResults.PSO.best_overall.best_params;
                setTunedParams(newTuned);""": """                if (fullResults.PSO?.best_overall) newTuned.PSO = fullResults.PSO.best_overall.best_params;
                if (fullResults.TPE?.best_overall) newTuned.TPE = fullResults.TPE.best_overall.best_params;
                if (fullResults["CMA-ES"]?.best_overall) newTuned["CMA-ES"] = fullResults["CMA-ES"].best_overall.best_params;
                if (fullResults.GWO?.best_overall) newTuned.GWO = fullResults.GWO.best_overall.best_params;
                setTunedParams(newTuned);""",
                
    # 8. mainSeries.push
    """    if (visiblePlots.PSO && compareResult?.PSO?.best_overall?.simData) mainSeries.push({ name: 'Best PSO', data: compareResult.PSO.best_overall.simData, colorP: '#10b981', colorY: '#6ee7b7' });""": """    if (visiblePlots.PSO && compareResult?.PSO?.best_overall?.simData) mainSeries.push({ name: 'Best PSO', data: compareResult.PSO.best_overall.simData, colorP: '#10b981', colorY: '#6ee7b7' });
    if (visiblePlots.TPE && compareResult?.TPE?.best_overall?.simData) mainSeries.push({ name: 'Best TPE', data: compareResult.TPE.best_overall.simData, colorP: '#ec4899', colorY: '#fbcfe8' });
    if (visiblePlots["CMA-ES"] && compareResult?.["CMA-ES"]?.best_overall?.simData) mainSeries.push({ name: 'Best CMA-ES', data: compareResult["CMA-ES"].best_overall.simData, colorP: '#8b5cf6', colorY: '#c4b5fd' });
    if (visiblePlots.GWO && compareResult?.GWO?.best_overall?.simData) mainSeries.push({ name: 'Best GWO', data: compareResult.GWO.best_overall.simData, colorP: '#f59e0b', colorY: '#fcd34d' });""",
    
    # 9. text
    "Compare Manual PID baseline against Auto-Tuned (GA, PSO, BO) controllers.": "Compare Manual PID baseline against Auto-Tuned controllers.",
    
    # 10. buttons
    """                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className="secondary-btn" onClick={() => setVisiblePlots({Manual:true, GA:true, PSO:true, BO:true, Target:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>""": """                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className={visiblePlots.TPE ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, TPE: !visiblePlots.TPE})} style={{padding: '4px 12px', fontSize: 12}}>TPE</button>
                   <button className={visiblePlots["CMA-ES"] ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, "CMA-ES": !visiblePlots["CMA-ES"]})} style={{padding: '4px 12px', fontSize: 12}}>CMA-ES</button>
                   <button className={visiblePlots.GWO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GWO: !visiblePlots.GWO})} style={{padding: '4px 12px', fontSize: 12}}>GWO</button>
                   <button className="secondary-btn" onClick={() => setVisiblePlots({Manual:true, GA:true, PSO:true, TPE:true, "CMA-ES":true, GWO:true, Target:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>""",
                   
    # 11. iteration blocks
    """            {/* Block 3: PSO Iterations */}
            <IterationChartBlock alg="PSO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />""": """            {/* Block 3: SOTA Iterations */}
            <IterationChartBlock alg="PSO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="TPE" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="CMA-ES" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="GWO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />"""
}

for k, v in replacements.items():
    if k not in content:
        print(f"Warning: Could not find key in content:\n{k[:50]}...")
    else:
        content = content.replace(k, v)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated frontend PageIdealTuning.jsx")
