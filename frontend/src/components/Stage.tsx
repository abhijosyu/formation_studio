import { useMemo, useState } from "react";
import type { Dancer, Point, TargetSlot } from "../types/domain";

type Props = {
  dancers: Dancer[];
  starts: Record<string, Point>;
  targets: TargetSlot[];
  onMove: (id: string, point: Point) => void;
  trails?: { dancer_id: string; points: Point[] }[];
  conflicts?: Point[];
};

const WIDTH = 860;
const HEIGHT = 520;
const STAGE_WIDTH = 16;
const STAGE_DEPTH = 10;

function screen(point: Point): Point {
  return { x: WIDTH / 2 + (point.x / STAGE_WIDTH) * WIDTH, y: HEIGHT / 2 - (point.y / STAGE_DEPTH) * HEIGHT };
}
function stage(point: Point): Point {
  return { x: ((point.x - WIDTH / 2) / WIDTH) * STAGE_WIDTH, y: -((point.y - HEIGHT / 2) / HEIGHT) * STAGE_DEPTH };
}

export function Stage({ dancers, starts, targets, onMove, trails = [], conflicts = [] }: Props) {
  const [dragging, setDragging] = useState<string | null>(null);
  const grid = useMemo(() => Array.from({ length: 17 }, (_, index) => index), []);
  const update = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!dragging) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const point = stage({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    onMove(dragging, { x: Math.max(-8, Math.min(8, point.x)), y: Math.max(-5, Math.min(5, point.y)) });
  };
  return <svg className="stage" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} onPointerMove={update} onPointerUp={() => setDragging(null)} onPointerLeave={() => setDragging(null)}>
    <rect width={WIDTH} height={HEIGHT} fill="#101a22" />
    {grid.map((index) => <line key={`v${index}`} x1={index * (WIDTH / 16)} x2={index * (WIDTH / 16)} y1="0" y2={HEIGHT} className="grid" />)}
    {Array.from({ length: 11 }, (_, index) => <line key={`h${index}`} y1={index * (HEIGHT / 10)} y2={index * (HEIGHT / 10)} x1="0" x2={WIDTH} className="grid" />)}
    <rect x="1" y="1" width={WIDTH - 2} height={HEIGHT - 2} className="stage-boundary" />
    {trails.map((path) => <polyline key={path.dancer_id} points={path.points.map((point) => { const p = screen(point); return `${p.x},${p.y}`; }).join(" ")} className="trail" />)}
    {targets.map((target) => { const p = screen(target.position); return <g key={target.id}><circle cx={p.x} cy={p.y} r="13" className="target" /><text x={p.x} y={p.y + 4} className="target-label">{target.id.replace("slot-", "T")}</text></g>; })}
    {dancers.map((dancer) => { const p = screen(starts[dancer.id]); return <g key={dancer.id} onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); setDragging(dancer.id); }} className="dancer"><circle cx={p.x} cy={p.y} r="16" /><text x={p.x} y={p.y + 4}>{dancer.label}</text></g>; })}
    {conflicts.map((point, index) => { const p = screen(point); return <circle key={`${p.x}-${p.y}-${index}`} cx={p.x} cy={p.y} r="8" className="conflict" />; })}
    <text x="14" y="25" className="scale">16m × 10m · 1m grid</text>
  </svg>;
}
