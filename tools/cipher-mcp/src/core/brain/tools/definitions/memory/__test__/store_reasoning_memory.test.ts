import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { storeReasoningMemoryTool } from '../store_reasoning_memory.js';
import { InternalToolContext } from '../../../types.js';

// Mock logger
vi.mock('../../../../logger/index.js', () => ({
	createLogger: vi.fn(() => ({
		debug: vi.fn(),
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	})),
}));

describe('storeReasoningMemoryTool', () => {
	let mockContext: InternalToolContext;
	let mockEmbedder: any;
	let mockVectorStore: any;
	let mockVectorStoreManager: any;

	beforeEach(() => {
		mockEmbedder = {
			embed: vi.fn().mockResolvedValue(
				Array(128)
					.fill(0)
					.map(() => Math.random())
			),
		};

		mockVectorStore = {
			insert: vi.fn().mockResolvedValue(true),
			search: vi.fn().mockResolvedValue([]),
			getBackendType: vi.fn().mockReturnValue('in-memory'),
			getDimension: vi.fn().mockReturnValue(128),
			getCollectionName: vi.fn().mockReturnValue('reflection_test'),
			isConnected: vi.fn().mockReturnValue(true),
			getCollectionInfo: vi.fn().mockResolvedValue({ vectors_count: 0, status: 'ok' }),
		};

		mockVectorStoreManager = {
			getStore: vi.fn((type?: string) => {
				if (type === 'reflection') {
					return mockVectorStore;
				}
				return mockVectorStore; // fallback
			}),
		};

		const mockEmbeddingManager = {
			getEmbedder: vi.fn().mockReturnValue(mockEmbedder),
		} as any;

		mockContext = {
			services: {
				embeddingManager: mockEmbeddingManager,
				vectorStoreManager: mockVectorStoreManager,
				llmService: undefined as any,
			},
			toolName: 'store_reasoning_memory',
			startTime: Date.now(),
			sessionId: 'test-session',
			metadata: {},
		};
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	describe('Tool Definition', () => {
		it('should have correct basic properties', () => {
			expect(storeReasoningMemoryTool.name).toBe('store_reasoning_memory');
			expect(storeReasoningMemoryTool.category).toBe('memory');
			expect(storeReasoningMemoryTool.internal).toBe(true);
			expect(typeof storeReasoningMemoryTool.handler).toBe('function');
		});

		it('should have correct parameter schema', () => {
			const schema = storeReasoningMemoryTool.parameters;
			expect(schema.type).toBe('object');
			expect(schema.required).toContain('trace');
			expect(schema.required).toContain('evaluation');
			expect(schema.properties.trace).toBeDefined();
			expect(schema.properties.evaluation).toBeDefined();
		});
	});

	describe('Tool Handler', () => {
		const validReasoningSteps = [
			{
				type: 'thought' as const,
				content: 'I need to analyze this problem step by step',
			},
			{
				type: 'action' as const,
				content: 'First, I will examine the code structure',
			},
		];

		const validTrace = {
			id: 'test-trace-123',
			steps: validReasoningSteps,
			metadata: {
				extractedAt: new Date().toISOString(),
				conversationLength: 5,
				stepCount: 2,
				hasExplicitMarkup: true,
				sessionId: 'test-session',
				taskContext: {
					goal: 'Analyze code structure',
					input: 'How to implement a feature',
					taskType: 'code_analysis',
					domain: 'programming',
					complexity: 'medium' as const,
				},
			},
		};

		const validEvaluation = {
			qualityScore: 0.8,
			efficiencyScore: 0.7,
			issues: [],
			suggestions: ['Consider adding more detailed analysis'],
			shouldStore: true,
		};

		it('should successfully store high-quality reasoning', async () => {
			const args = {
				trace: validTrace,
				evaluation: validEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, mockContext);

			expect(result.success).toBe(true);
			expect(result.result.stored).toBe(true);
			expect(result.metadata.vectorId).toBeDefined();
			expect(mockEmbedder.embed).toHaveBeenCalledOnce();
			expect(mockVectorStore.insert).toHaveBeenCalledOnce();
		});

		it('should skip storage for low-quality reasoning', async () => {
			const lowQualityEvaluation = {
				...validEvaluation,
				shouldStore: false,
			};

			const args = {
				trace: validTrace,
				evaluation: lowQualityEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, mockContext);

			expect(result.success).toBe(true);
			expect(result.result.stored).toBe(false);
			expect(result.result.message).toContain('quality threshold');
			expect(mockVectorStore.insert).not.toHaveBeenCalled();
		});

		it('should store when shouldStore is true regardless of quality score', async () => {
			const lowQualityEvaluation = {
				...validEvaluation,
				qualityScore: 0.3,
				shouldStore: true, // Override low quality score
			};

			const args = {
				trace: validTrace,
				evaluation: lowQualityEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, mockContext);

			expect(result.success).toBe(true);
			expect(result.result.stored).toBe(true);
			expect(mockVectorStore.insert).toHaveBeenCalledOnce();
		});

		it('should handle missing required services gracefully', async () => {
			const contextWithoutServices = {
				...mockContext,
				services: undefined as any,
			};

			const args = {
				trace: validTrace,
				evaluation: validEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, contextWithoutServices);

			expect(result.success).toBe(false);
			expect(result.result.stored).toBe(false);
			expect(result.result.error).toContain('Services context is required');
		});

		it('should handle invalid input gracefully', async () => {
			const invalidTrace = {
				...validTrace,
				steps: [], // Empty array
			};

			const args = {
				trace: invalidTrace,
				evaluation: validEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, mockContext);

			expect(result.success).toBe(false);
			expect(result.result.stored).toBe(false);
			expect(result.result.error).toContain('steps array is empty');
		});

		it('should handle dual collection manager correctly', async () => {
			// Test with dual collection manager that supports getStore('reflection')
			const dualCollectionManager = {
				getStore: vi.fn((type?: string) => {
					if (type === 'reflection') {
						return mockVectorStore;
					}
					return mockVectorStore; // Return same store for fallback
				}),
				isConnected: vi.fn().mockReturnValue(true),
			};

			const contextWithDualManager = {
				...mockContext,
				services: {
					...mockContext.services!,
					vectorStoreManager: dualCollectionManager as any,
				},
			};

			const args = {
				trace: validTrace,
				evaluation: validEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, contextWithDualManager);

			expect(result.success).toBe(true);
			expect(result.result.stored).toBe(true);
			expect(dualCollectionManager.getStore).toHaveBeenCalledWith('reflection');
		});

		it('should fall back to default store when reflection store is not available', async () => {
			// Test with manager that returns null for reflection store
			const managerWithoutReflection = {
				getStore: vi.fn((type?: string) => {
					if (type === 'reflection') {
						return null; // No reflection store
					}
					return mockVectorStore; // Default store available
				}),
			};

			const contextWithoutReflection = {
				...mockContext,
				services: {
					...mockContext.services!,
					vectorStoreManager: managerWithoutReflection as any,
				},
			};

			const args = {
				trace: validTrace,
				evaluation: validEvaluation,
			};

			const result = await storeReasoningMemoryTool.handler(args, contextWithoutReflection);

			expect(result.success).toBe(true);
			expect(result.result.stored).toBe(true);
			expect(managerWithoutReflection.getStore).toHaveBeenCalledWith('reflection');
			// Should fall back to default store and succeed
		});
	});
});
