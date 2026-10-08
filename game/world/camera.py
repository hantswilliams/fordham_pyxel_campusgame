def follow(target_x: float, target_y: float, view_w: int, view_h: int,
           world_w: int, world_h: int) -> tuple[int, int]:
    """Camera top-left that centres the target, clamped to the world edges.
    If the world is smaller than the view on an axis, it is centred."""

    def axis(target: float, view: int, world: int) -> int:
        if world <= view:
            return -(view - world) // 2
        return int(max(0, min(target - view // 2, world - view)))

    return axis(target_x, view_w, world_w), axis(target_y, view_h, world_h)
