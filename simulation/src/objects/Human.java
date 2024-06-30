package simulation.src.objects;
class Human {
    private int health;
    private int age;
    private Weapon weapon;

    public Human(){
        health = 100;
        age = 1;
        weapon = new Weapon(false);
    }

    
}
