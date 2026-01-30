def max_points(tile_multipliers):
    # Add boundary tiles with value 1 as per rules [cite: 518-519]
    nums = [1] + tile_multipliers + [1]
    n = len(nums)
    
    # dp[i][j] stores max points for range (i, j) exclusive
    dp = [[0] * n for _ in range(n)]
    
    # Length of the range being considered
    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            
            # Iterate through all possible last shattered tiles 'k' between left and right
            for k in range(left + 1, right):
                # Points gained = points from left side + points from right side + shattering k last
                points = dp[left][k] + dp[k][right] + (nums[left] * nums[k] * nums[right])
                dp[left][right] = max(dp[left][right], points)
                
    return dp[0][n-1]

def solve_task2():
    # Example 1 [cite: 526]
    example1 = [3, 1, 5, 8]
    print(f"Example 1 Result: {max_points(example1)} (Expected: 167)")
    
    # Example 2 [cite: 535]
    example2 = [1, 5]
    print(f"Example 2 Result: {max_points(example2)} (Expected: 10)")

if __name__ == "__main__":
    solve_task2()