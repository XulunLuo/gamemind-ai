// Controls Granny's chasing behavior and attack logic
public class GrannyAI : MonoBehaviour {
    public float chaseSpeed = 3f;
    public float attackRange = 1.5f;
    private Transform player;

    void Start() {
        player = GameObject.FindWithTag("Player").transform;
    }

    void Update() {

        // Chase the player
        float distanceToPlayer = Vector3.Distance(transform.position, player.position);
        
        if (distanceToPlayer > attackRange) {

            // Move toward player
            transform.position = Vector3.MoveTowards(
                transform.position, 
                player.position, 
                chaseSpeed * Time.deltaTime
            );
        } else {
            
            // Attack!
            Attack();
        }
    }

    void Attack() {
        Debug.Log("Granny attacks!");
    }
}