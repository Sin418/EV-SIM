package simulation.src.objects;
import java.util.Random;

public class Weapon {
    private Boolean fist;
    private int health;
    private int dammage;

    public Weapon(Boolean hasWeapon){
        if (hasWeapon){
            Random rand = new Random();
            int rand1 = rand.nextInt(6,10);
            int rand2 = rand.nextInt(20,30);
            health = rand1;
            dammage = rand2;
            fist = false;
        }
        else{
            health = 0;
            dammage = 0;
            fist = true;
        }

    }

    public int getHealth(){
        return health;
        
    }
    public int getDammage(){
        return dammage;
    }
    public boolean getFist(){
        return fist;
    }


}
