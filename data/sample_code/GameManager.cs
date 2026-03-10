// Manages overall game state 
public class GameManager : MonoBehaviour {
    public static GameManager Instance;
    public int score = 0;
    public bool gameOver = false;

    void Awake() {
        // Singleton — only one GameManager exists at a time
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    public void AddScore(int points) {
        score += points;
    }

    public void TriggerGameOver() {
        gameOver = true;
        Debug.Log("Game Over! Final score: " + score);
    }
}