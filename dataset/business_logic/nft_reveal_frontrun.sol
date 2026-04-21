// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: NFT Reveal Front-Running via Predictable Randomness
 * CATEGORY: Business Logic — Weak Randomness / Front-Running
 *
 * Token traits are assigned using blockhash(block.number - 1) and
 * block.timestamp. Both are known to validators before the reveal
 * transaction is included. A validator (or MEV bot watching the pending tx)
 * can selectively include or reorder the reveal to pick a desirable trait,
 * or simply delay until the right block appears.
 */
contract NFTRevealFrontrun {
    uint256 public constant MAX_SUPPLY = 10_000;
    mapping(uint256 => uint8)  public tokenRarity; // 0=common, 1=rare, 2=legendary
    mapping(uint256 => address) public ownerOf;
    uint256 public nextTokenId;
    uint256 public mintPrice = 0.08 ether;

    function mint() external payable returns (uint256 tokenId) {
        require(nextTokenId < MAX_SUPPLY, "Sold out");
        require(msg.value >= mintPrice, "Wrong price");
        tokenId = nextTokenId++;
        ownerOf[tokenId] = msg.sender;
        // Reveal deferred to revealToken()
    }

    function revealToken(uint256 tokenId) external {
        require(ownerOf[tokenId] == msg.sender, "Not owner");
        // BUG: uses block data know to miner/validator before tx is mined
        uint256 seed = uint256(keccak256(abi.encodePacked(
            blockhash(block.number - 1),   // known at mine time
            block.timestamp,               // manipulable ±15s
            tokenId,
            msg.sender
        )));
        // 1% legendary, 10% rare, 89% common
        uint8 rarity = seed % 100 < 1 ? 2 : (seed % 100 < 11 ? 1 : 0);
        tokenRarity[tokenId] = rarity;
    }
}
