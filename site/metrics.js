export function summarise(rows,year='All',severity='All') {
 return rows.filter(r=>(year==='All'||r.year===Number(year))&&(severity==='All'||r.severity===severity)).reduce((a,r)=>({crashes:a.crashes+r.crashes,serious_crashes:a.serious_crashes+r.serious_crashes,serious_casualties:a.serious_casualties+r.serious_casualties}),{crashes:0,serious_crashes:0,serious_casualties:0});
}
export function comparison(rows,k,method){return rows.find(r=>r.k===Number(k)&&r.method===method)||null;}
export const MANAGERS={state:'State-controlled (TMR)',council:'Council',mixed:'Mixed'};
export function managerText(cell){const c=cell.authority_counts,coded=c.state+c.council;
 if(!coded)return 'Not coded';
 return cell.manager==='council'?`Council: ${c.council} of ${coded} crashes`:cell.manager==='state'?`State: ${c.state} of ${coded} crashes`:`Mixed: ${c.state} state, ${c.council} council`;}
export function shortlistRows(results,roads,list,k){
 if(list==='all')return results.shortlist.slice(0,k).map(r=>({rank:r.rank,cell_id:r.cell_id,train:r.serious_count,holdout:r.holdout_serious_count,suburbs:r.suburbs}));
 const own=roads.by_manager.find(m=>m.manager===list);
 if(!own)throw Error(`unknown road list ${list}`);
 return own.own_shortlist.slice(0,k).map(r=>({rank:r.rank,cell_id:r.cell_id,train:r.training_serious,holdout:r.holdout_serious,suburbs:roads.cells[r.cell_id].suburbs.join(', ')}));
}
