package simulation.src.scene;

import javax.swing.JPanel;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.FileWriter;
import java.io.IOException;
import javax.imageio.ImageIO;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

public class GamePanel extends JPanel {
    private BufferedImage[] grassSprites;
    private BufferedImage waterSprite;
    private BufferedImage topSprite;
    private BufferedImage movableSprite;
    private BufferedImage background;
    private static final int SPRITE_WIDTH = 64;
    private static final int SPRITE_HEIGHT = 31;
    private static final int PANEL_WIDTH = 1920;
    private static final int PANEL_HEIGHT = 1080;
    private boolean[][] topSpritePositions;
    private boolean[][] waterPositions;
    private List<DynamicSprite> dynamicSprites;
    private MovableSprite player;
    private MapState mapState = new MapState();

    public GamePanel() {
        setPreferredSize(new Dimension(PANEL_WIDTH, PANEL_HEIGHT));
        loadSprites();
        generateBackground();
        generateTopSpritePositions();
        dynamicSprites = new ArrayList<>();
        player = new MovableSprite(PANEL_WIDTH / 2, PANEL_HEIGHT / 2); 

        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                switch (e.getKeyCode()) {
                    case KeyEvent.VK_W:
                        player.moveUp();
                        break;
                    case KeyEvent.VK_A:
                        player.moveLeft();
                        break;
                    case KeyEvent.VK_S:
                        player.moveDown();
                        break;
                    case KeyEvent.VK_D:
                        player.moveRight();
                        break;
                }
                repaint();
            }
        });
        setFocusable(true);
        requestFocusInWindow();
    }

    private void loadSprites() {
        grassSprites = new BufferedImage[4];
        try {
            for (int i = 0; i < 4; i++) {
                grassSprites[i] = ImageIO.read(getClass().getResource("/simulation/sprites/plain_grass" + (i + 1) + ".png"));
            }
            waterSprite = ImageIO.read(getClass().getResource("/simulation/sprites/plain_water1.png"));
            topSprite = ImageIO.read(getClass().getResource("/simulation/sprites/plant1.png"));
            movableSprite = ImageIO.read(getClass().getResource("/simulation/sprites/Blue_left.png")); 
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void generateBackground() {
        background = new BufferedImage(PANEL_WIDTH, PANEL_HEIGHT, BufferedImage.TYPE_INT_ARGB);
        Graphics g = background.getGraphics();
        Random random = new Random();

        int cols = PANEL_WIDTH / SPRITE_WIDTH + 2; 
        int rows = PANEL_HEIGHT / (SPRITE_HEIGHT / 2) + 2; 
        waterPositions = new boolean[rows][cols];

        
        for (int y = 0; y < rows; y++) {
            for (int x = 0; x < cols; x++) {
                int xPos = x * SPRITE_WIDTH;
                int yPos = y * (SPRITE_HEIGHT / 2) - SPRITE_HEIGHT / 2; 
                if (y % 2 != 0) {
                    xPos -= SPRITE_WIDTH / 2;
                }
                boolean isWater = random.nextInt(12) == 0; 
                BufferedImage bottomSprite;
                String type;
                if (isWater) {
                    bottomSprite = waterSprite;
                    type = "water";
                    waterPositions[y][x] = true;
                } else {
                    bottomSprite = grassSprites[random.nextInt(grassSprites.length)];
                    type = "grass";
                    waterPositions[y][x] = false;
                }
                g.drawImage(bottomSprite, xPos, yPos, null);
                mapState.tiles.add(new MapState.Tile(xPos, yPos, type, false));
            }
        }
        g.dispose();
    }

    private void generateTopSpritePositions() {
        int cols = PANEL_WIDTH / SPRITE_WIDTH + 2; 
        int rows = PANEL_HEIGHT / (SPRITE_HEIGHT / 2) + 2; 
        topSpritePositions = new boolean[rows][cols];
        Random random = new Random();

        for (int y = 0; y < rows; y++) {
            for (int x = 0; x < cols; x++) {
                if (!waterPositions[y][x]) {
                    topSpritePositions[y][x] = random.nextInt(17) == 0; 
                    if (topSpritePositions[y][x]) {
                        int xPos = x * SPRITE_WIDTH;
                        int yPos = y * (SPRITE_HEIGHT / 2) - SPRITE_HEIGHT / 2; 
                        if (y % 2 != 0) {
                            xPos -= SPRITE_WIDTH / 2;
                        }
                        for (MapState.Tile tile : mapState.tiles) {
                            if (tile.x == xPos && tile.y == yPos) {
                                tile.hasTopSprite = true;
                                break;
                            }
                        }
                    }
                } else {
                    topSpritePositions[y][x] = false;
                }
            }
        }
    }

    public void addDynamicSprite(int x, int y) {
        dynamicSprites.add(new DynamicSprite(x, y));
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        mapState.tiles.clear();

        g.drawImage(background, 0, 0, null);

        int cols = getWidth() / SPRITE_WIDTH + 2; 
        int rows = getHeight() / (SPRITE_HEIGHT / 2) + 2; 

        for (int y = 0; y < rows; y++) {
            for (int x = 0; x < cols; x++) {
                int xPos = x * SPRITE_WIDTH;
                int yPos = y * (SPRITE_HEIGHT / 2) - SPRITE_HEIGHT / 2; 
                if (y % 2 != 0) {
                    xPos -= SPRITE_WIDTH / 2;
                }
                String type = waterPositions[y][x] ? "water" : "grass";
                boolean hasTopSprite = topSpritePositions[y][x];
                mapState.tiles.add(new MapState.Tile(xPos, yPos, type, hasTopSprite));
                if (hasTopSprite) {
                    g.drawImage(topSprite, xPos, yPos, null);
                }
            }
        }

        for (DynamicSprite sprite : dynamicSprites) {
            g.drawImage(topSprite, sprite.getX(), sprite.getY(), null);
        }

        g.drawImage(movableSprite, player.getX(), player.getY(), null);

        saveMapStateToJson("state/map_state.json"); 
    }

    private void saveMapStateToJson(String filename) {
    try (FileWriter writer = new FileWriter(filename)) {
        writer.write("{");

        writer.write("\"grass\":[");
        boolean first = true;
        for (MapState.Tile tile : mapState.tiles) {
            if (tile.type.equals("grass")) {
                if (!first) writer.write(",");
                writer.write("{\"x\":" + tile.x + ",\"y\":" + tile.y + ",\"hasTopSprite\":" + tile.hasTopSprite + "}");
                first = false;
            }
        }
        writer.write("],");

        writer.write("\"water\":[");
        first = true;
        for (MapState.Tile tile : mapState.tiles) {
            if (tile.type.equals("water")) {
                if (!first) writer.write(",");
                writer.write("{\"x\":" + tile.x + ",\"y\":" + tile.y + "}");
                first = false;
            }
        }
        writer.write("],");

        writer.write("\"topSprites\":[");
        first = true;
        for (MapState.Tile tile : mapState.tiles) {
            if (tile.hasTopSprite) {
                if (!first) writer.write(",");
                writer.write("{\"x\":" + tile.x + ",\"y\":" + tile.y + "}");
                first = false;
            }
        }
        writer.write("],");

        writer.write("\"characters\":[");
        writer.write("{\"x\":" + player.getX() + ",\"y\":" + player.getY() + "}");
        writer.write("]");

        writer.write("}");
    } catch (IOException e) {
        e.printStackTrace();
    }
}


    private class DynamicSprite {
        private int x;
        private int y;

        public DynamicSprite(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public int getX() {
            return x;
        }

        public int getY() {
            return y;
        }
    }

    private class MovableSprite {
        private int x;
        private int y;
        private final int SPEED = 5;

        public MovableSprite(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public void moveUp() {
            y -= SPEED;
        }

        public void moveDown() {
            y += SPEED;
        }

        public void moveLeft() {
            x -= SPEED;
        }

        public void moveRight() {
            x += SPEED;
        }

        public int getX() {
            return x;
        }

        public int getY() {
            return y;
        }
    }
}
