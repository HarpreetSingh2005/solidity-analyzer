// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Airdrop based on NFT holdings can be drained using flash-loaned NFTs.
contract VulnNewFlashAirdrop {
    // Doesn't verify how long the user has held the NFT
}