package simulation.src.scene;

import javax.swing.JPanel;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;
import javax.imageio.ImageIO;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class GamePanel extends JPanel {
    private BufferedImage[] bottomSprites;
    private BufferedImage topSprite;
    private BufferedImage background;
    private static final int SPRITE_WIDTH = 64;
    private static final int SPRITE_HEIGHT = 31;
    private static final int PANEL_WIDTH = 1920; 
    private static final int PANEL_HEIGHT = 1080;
    private boolean[][] topSpritePositions;
    private List<DynamicSprite> dynamicSprites;

    public GamePanel() {
        setPreferredSize(new Dimension(PANEL_WIDTH, PANEL_HEIGHT));
        loadSprites();
        generateBackground();
        generateTopSpritePositions();
        dynamicSprites = new ArrayList<>();
    }

    private void loadSprites() {
        bottomSprites = new BufferedImage[4];
        try {
            for (int i = 0; i < 4; i++) {
                bottomSprites[i] = ImageIO.read(getClass().getResource("/simulation/sprites/plain_grass" + (i + 1) + ".png"));
            }
            topSprite = ImageIO.read(getClass().getResource("/simulation/sprites/plant1.png")); 
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

        for (int y = -1; y < rows; y++) { 
            for (int x = 0; x < cols; x++) {
                int xPos = x * SPRITE_WIDTH;
                int yPos = y * (SPRITE_HEIGHT / 2);
              
                if (y % 2 != 0) {
                    xPos -= SPRITE_WIDTH / 2;
                }
                BufferedImage bottomSprite = bottomSprites[random.nextInt(bottomSprites.length)];
                g.drawImage(bottomSprite, xPos, yPos, null);
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
                topSpritePositions[y][x] = random.nextInt(17) == 0; 
            }
        }
    }

    public void addDynamicSprite(int x, int y) {
        dynamicSprites.add(new DynamicSprite(x, y));
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        g.drawImage(background, 0, 0, null);

        int cols = getWidth() / SPRITE_WIDTH + 2; 
        int rows = getHeight() / (SPRITE_HEIGHT / 2) + 2; 

        for (int y = 0; y < rows; y++) {
            for (int x = 0; x < cols; x++) {
                int xPos = x * SPRITE_WIDTH;
                int yPos = y * (SPRITE_HEIGHT / 2);
            
                if (y % 2 != 0) {
                    xPos -= SPRITE_WIDTH / 2;
                }
                if (topSpritePositions[y][x]) {
                    g.drawImage(topSprite, xPos, yPos, null);
                }
            }
        }

        for (DynamicSprite sprite : dynamicSprites) {
            g.drawImage(topSprite, sprite.getX(), sprite.getY(), null);
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
}
