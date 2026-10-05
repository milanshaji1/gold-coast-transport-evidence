export function summarise(rows,year='All',severity='All') {
 return rows.filter(r=>(year==='All'||r.year===Number(year))&&(severity==='All'||r.severity===severity)).reduce((a,r)=>({crashes:a.crashes+r.crashes,serious_crashes:a.serious_crashes+r.serious_crashes,serious_casualties:a.serious_casualties+r.serious_casualties}),{crashes:0,serious_crashes:0,serious_casualties:0});
}
export function comparison(rows,k,method){return rows.find(r=>r.k===Number(k)&&r.method===method)||null;}
