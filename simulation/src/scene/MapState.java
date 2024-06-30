package simulation.src.scene;

import java.util.ArrayList;
import java.util.List;

public class MapState {
    public List<Tile> tiles = new ArrayList<>();

    public static class Tile {
        public int x;
        public int y;
        public String type;
        public boolean hasTopSprite;

        public Tile(int x, int y, String type, boolean hasTopSprite) {
            this.x = x;
            this.y = y;
            this.type = type;
            this.hasTopSprite = hasTopSprite;
        }
    }
}

