<?php
/**
 * Blog post template (post type "post", permalinks prefixed /blog/ via the
 * site's Permalinks setting -- see README). Body content (H2 sections, FAQ,
 * comparison tables) comes from post_content as migrated/generated; this
 * template just frames it consistently with a meta line and a related-posts
 * rail, matching the old site's per-post structure.
 */
defined( 'ABSPATH' ) || exit;
get_header();

while ( have_posts() ) :
	the_post();
	?>
	<article class="bb-section bb-container" style="max-width:760px;">
		<h1><?php the_title(); ?></h1>
		<p class="bb-post-meta">
			<?php echo esc_html( get_the_date() ); ?>
		</p>

		<div class="bb-post-content">
			<?php the_content(); ?>
		</div>

		<?php
		$related = new WP_Query(
			array(
				'post_type'      => 'post',
				'posts_per_page' => 3,
				'post__not_in'   => array( get_the_ID() ),
				'orderby'        => 'rand',
			)
		);
		if ( $related->have_posts() ) :
			?>
			<div class="bb-related-posts">
				<h2><?php esc_html_e( 'Related Blog Posts', 'bizbot' ); ?></h2>
				<div class="bb-post-grid">
					<?php
					while ( $related->have_posts() ) :
						$related->the_post();
						?>
						<a class="bb-post-card" href="<?php the_permalink(); ?>">
							<?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'medium' ); } ?>
							<div class="bb-post-card-body">
								<h3 style="font-size:1rem;margin:0;"><?php the_title(); ?></h3>
							</div>
						</a>
					<?php endwhile; ?>
				</div>
			</div>
			<?php
			wp_reset_postdata();
		endif;
		?>
	</article>
	<?php
endwhile;

get_footer();
