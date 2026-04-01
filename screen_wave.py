import pygame


def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    left_margin, right_margin, top_margin, bottom_margin = 140, 40, 40, 50
    plot_width = rect.width - left_margin - right_margin
    plot_height = rect.height - top_margin - bottom_margin

    neurons = list(sim.neuron_data.keys())
    if not neurons:
        sim.draw_text(surface, "Aucun neurone sélectionné.", left_margin, top_margin, color=sim.WHITE, font_size=24)
        return

    max_points = max(50, plot_width)
    window = min(max_points, max(1, sim.iteration))
    scale_x = plot_width / max(1, window - 1)

    vals=[]
    for n in neurons:
        vals.extend(sim.neuron_data[n].get('values', [])[-window:])
    vmin=min(vals) if vals else 0
    vmax=max(vals) if vals else 1
    if vmax-vmin<1e-6:
        vmax=vmin+1

    pygame.draw.line(surface, sim.WHITE, (left_margin, top_margin), (left_margin, rect.height-bottom_margin))
    pygame.draw.line(surface, sim.WHITE, (left_margin, rect.height-bottom_margin), (rect.width-right_margin, rect.height-bottom_margin))

    for idx,n in enumerate(neurons):
        data=sim.neuron_data[n].get('values', [])[-window:]
        color=sim.neuron_data[n]['color']
        sim.draw_text(surface,n,10,top_margin+idx*22,color=color,font_size=16)
        pts=[]
        for i,v in enumerate(data):
            x=left_margin+i*scale_x
            y=top_margin+plot_height-( (v-vmin)/(vmax-vmin) )*plot_height
            pts.append((x,y))
        if len(pts)>1:
            pygame.draw.lines(surface,color,False,pts,1)

    for i,val in enumerate([vmin,(vmin+vmax)/2,vmax]):
        y=top_margin+plot_height-(i/2)*plot_height
        sim.draw_text(surface,f"{val:.2f}",90,y-10,color=sim.WHITE,font_size=14)

    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", rect.width-220, 10)
