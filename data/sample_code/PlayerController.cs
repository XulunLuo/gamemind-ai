// Handles all player (Capybara) movement and input
public class PlayerController : MonoBehaviour {
    public float speed = 5f;
    public float jumpForce = 8f;
    private Rigidbody rb;

    void Start() {
        rb = GetComponent<Rigidbody>();
    }

    void Update() {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");
        transform.Translate(new Vector3(h, 0, v) * speed * Time.deltaTime);

        if (Input.GetKeyDown(KeyCode.Space)) {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }
}