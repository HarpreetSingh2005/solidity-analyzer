// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: ERC-4626 Vault Share Inflation / First Depositor Attack
 * CATEGORY: Flash Loan — Share Price Manipulation
 *
 * Classic vault inflation attack amplified by flash loans:
 * 1. Flash borrow large ETH amount
 * 2. Become first depositor → receive 1 share for 1 ETH
 * 3. Directly donate a huge ETH amount to the vault (no shares minted)
 * 4. New depositor's shares round down to 0 (1 ETH → 0 shares)
 * 5. Withdraw the 1 share → get original ETH + victim's ETH
 * 6. Repay flash loan → profit
 */
contract ShareInflation {
    uint256 public totalAssets;
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    uint256 private constant OFFSET = 0; // BUG: no virtual offset protection

    function deposit() external payable {
        uint256 newShares;
        if (totalShares == 0) {
            newShares = msg.value; // First depositor: 1 share per wei
        } else {
            // BUG: integer division floors to 0 when totalAssets is huge
            newShares = (msg.value * totalShares) / totalAssets;
        }
        require(newShares > 0, "Zero shares"); // BUG: this can be bypassed if victim's tx is the "second" with inflated totalAssets
        shares[msg.sender] += newShares;
        totalShares        += newShares;
        totalAssets        += msg.value;
    }

    // Donate ETH directly — inflates asset/share ratio without minting shares
    // BUG: no protection against direct donation inflating totalAssets
    receive() external payable {
        totalAssets += msg.value;
    }

    function withdraw() external {
        uint256 userShares = shares[msg.sender];
        require(userShares > 0, "No shares");
        uint256 ethAmount          = (userShares * totalAssets) / totalShares;
        shares[msg.sender]  = 0;
        totalShares        -= userShares;
        totalAssets        -= ethAmount;
        payable(msg.sender).transfer(ethAmount);
    }
}
