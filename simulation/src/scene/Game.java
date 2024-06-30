package simulation.src.scene;

import javax.swing.JFrame;

public class Game extends JFrame implements Runnable {

    private GamePanel gamePanel;

    public Game() {
        gamePanel = new GamePanel();
        add(gamePanel);
        pack();
        setTitle("2D Sprite Render");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        setLocationRelativeTo(null);
        setVisible(true);
    }

    public static void main(String[] args) {
        Game game = new Game();
        new Thread(game).start();
    }

    @Override
    public void run() {
        while (true) {
            gamePanel.repaint();
            try {
                Thread.sleep(16); 
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
